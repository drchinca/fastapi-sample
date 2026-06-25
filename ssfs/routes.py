"""Marketo SSFS — Adobe owns the path names and JSON keys here."""

import json
import logging
import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Response
from fastapi.responses import JSONResponse

from auth_methods.auth import require_marketo_basic
from utils.users import random_email, random_name

logger = logging.getLogger(__name__)

router = APIRouter(tags=["marketo"])

OPENAPI_PATH = Path(__file__).resolve().parent / "openapi.json"

SERVICE_DEF: dict[str, Any] = {
    "apiName": "random-user-poc",
    "i18n": {
        "en_US": {
            "name": "Random User Email",
            "description": "Assigns a random name and email to the lead.",
            "triggerName": "Random Email Assigned",
            "filterName": "Random Email Was Assigned",
        }
    },
    "primaryAttribute": "label",
    "invocationPayloadDef": {
        "flowAttributes": [
            {
                "apiName": "label",
                "dataType": "string",
                "i18n": {"en_US": {"name": "Activity Label"}},
            }
        ],
        "userDrivenMapping": False,
        "fields": [],
    },
    "callbackPayloadDef": {
        "attributes": [
            {
                "apiName": "generated_email",
                "dataType": "email",
                "i18n": {"en_US": {"name": "Generated Email"}},
            },
            {
                "apiName": "generated_name",
                "dataType": "string",
                "i18n": {"en_US": {"name": "Generated Name"}},
            },
        ],
        "fields": [],
        "userDrivenMapping": False,
    },
}


def load_openapi() -> dict[str, Any]:
    spec = json.loads(OPENAPI_PATH.read_text())
    if base := os.getenv("API_BASE_URL", "").strip():
        spec["servers"] = [{"url": base.rstrip("/")}]
    elif domain := os.getenv("REPLIT_DEV_DOMAIN", "").strip():
        spec["servers"] = [{"url": f"https://{domain}"}]
    return spec


@router.get(
    "/install",
    summary="OpenAPI spec for Marketo SSFS registration",
    description=(
        "Marketo admins paste this URL into the SSFS install screen. "
        "Returns the provider's OpenAPI 3.0 spec with `servers[].url` rewritten "
        "to the current public host (via `API_BASE_URL` or `REPLIT_DEV_DOMAIN`). "
        "No auth required — Marketo fetches this before credentials exist."
    ),
    responses={
        200: {
            "description": "OpenAPI 3.0 document describing this SSFS service.",
            "content": {
                "application/json": {
                    "example": {
                        "openapi": "3.0.3",
                        "info": {"title": "Random User POC", "version": "1.0.0"},
                        "servers": [{"url": "https://your-replit.repl.co"}],
                        "paths": {"/submitAsyncAction": {"post": {"...": "..."}}},
                    }
                }
            },
        }
    },
)
def install() -> JSONResponse:
    """Return the OpenAPI spec Marketo uses to register this service."""
    return JSONResponse(load_openapi())


@router.get(
    "/getServiceDefinition",
    dependencies=[Depends(require_marketo_basic)],
    summary="Service metadata Marketo renders in the flow-step UI",
    description=(
        "Called by Marketo after install to learn this service's name, i18n labels, "
        "input attributes (shown in the Smart Campaign flow-step config), and output "
        "attributes (made available as tokens downstream). Requires HTTP Basic auth "
        "with the credentials configured via `MARKETO_USER` / `MARKETO_PASSWORD`."
    ),
    responses={
        200: {
            "description": "Service definition consumed by the Marketo SSFS UI.",
            "content": {
                "application/json": {
                    "example": {
                        "apiName": "random-user-poc",
                        "i18n": {"en_US": {"name": "Random User Email"}},
                        "primaryAttribute": "label",
                        "invocationPayloadDef": {"flowAttributes": [{"apiName": "label", "dataType": "string"}]},
                        "callbackPayloadDef": {
                            "attributes": [
                                {"apiName": "generated_email", "dataType": "email"},
                                {"apiName": "generated_name", "dataType": "string"},
                            ]
                        },
                    }
                }
            },
        },
        401: {"description": "Missing or invalid Basic auth credentials."},
    },
)
def get_service_definition() -> dict[str, Any]:
    """Return this service's metadata (name, input/output schemas) for Marketo's UI."""
    return SERVICE_DEF


@router.get(
    "/status",
    dependencies=[Depends(require_marketo_basic)],
    summary="Health check Marketo polls to confirm the service is reachable",
    description=(
        "Lightweight liveness probe Marketo calls periodically. "
        "Returns a free-form `info` array of human-readable status lines. "
        "Requires Basic auth."
    ),
    responses={
        200: {
            "description": "Service is up.",
            "content": {
                "application/json": {
                    "example": {"info": ["Random User POC is running."]}
                }
            },
        },
        401: {"description": "Missing or invalid Basic auth credentials."},
    },
)
def status() -> dict[str, list[str]]:
    """Return liveness info for Marketo's status check."""
    return {"info": ["Random User POC is running."]}


def _post_callback(callback_url: str, callback_key: str, token: str, body: dict[str, Any]) -> None:
    """Fire-and-log callback to Marketo; SSFS spec requires async delivery."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                callback_url,
                headers={
                    "x-api-key": callback_key,
                    "x-callback-token": token,
                    "Content-Type": "application/json",
                },
                json=body,
            )
        if not resp.is_success:
            logger.error("Marketo callback failed: status=%s body=%s", resp.status_code, resp.text)
        else:
            logger.info("Marketo callback delivered: status=%s", resp.status_code)
    except httpx.HTTPError as exc:
        logger.exception("Marketo callback error: %s", exc)


@router.post(
    "/submitAsyncAction",
    status_code=201,
    dependencies=[Depends(require_marketo_basic)],
    summary="Marketo flow-step invocation (async)",
    description=(
        "Marketo POSTs a batch of leads here when a Smart Campaign triggers the flow step. "
        "This endpoint **must** ack with 201 immediately — synchronous processing is not "
        "allowed per SSFS spec. The actual work runs in a background task that POSTs the "
        "result back to `callbackUrl` with the `x-api-key` and `x-callback-token` headers.\n\n"
        "**Required payload fields**: `callbackUrl`, `apiCallBackKey`, `token`.\n"
        "**Auth**: HTTP Basic (`MARKETO_USER` / `MARKETO_PASSWORD`)."
    ),
    responses={
        201: {"description": "Request accepted; callback will be delivered asynchronously."},
        400: {
            "description": "Missing required field (`callbackUrl`, `apiCallBackKey`, or `token`).",
            "content": {
                "application/json": {
                    "example": {"error": "callbackUrl, apiCallBackKey, and token are required"}
                }
            },
        },
        401: {"description": "Missing or invalid Basic auth credentials."},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "callbackUrl": "https://app-sjqe.marketo.com/rest/v1/leads/ssfs/callback",
                        "apiCallBackKey": "ABC123-callback-key",
                        "token": "one-time-callback-token",
                        "context": {"subscription": {"munchkinId": "123-ABC-456"}},
                        "flowAttributes": [{"apiName": "label", "value": "demo-run"}],
                        "objectData": [
                            {"objectContext": {"id": 1001}, "leadData": {"email": "alice@example.com"}},
                            {"objectContext": {"id": 1002}, "leadData": {"email": "bob@example.com"}},
                        ],
                    }
                }
            }
        }
    },
)
def submit_async_action(payload: dict[str, Any], background_tasks: BackgroundTasks) -> Response:
    """Accept a Marketo lead batch, ack 201, and deliver results via background callback."""
    callback_url = payload.get("callbackUrl")
    callback_key = payload.get("apiCallBackKey")
    token = payload.get("token")
    if not all((callback_url, callback_key, token)):
        return JSONResponse(
            status_code=400,
            content={"error": "callbackUrl, apiCallBackKey, and token are required"},
        )

    object_data = [
        {
            "leadData": {"id": item.get("objectContext", {}).get("id")},
            "activityData": {
                "generated_email": random_email(),
                "generated_name": random_name(),
                "success": True,
            },
        }
        for item in payload.get("objectData", [])
    ]

    body = {
        "munchkinId": payload.get("context", {}).get("subscription", {}).get("munchkinId", ""),
        "objectData": object_data,
    }

    background_tasks.add_task(_post_callback, callback_url, callback_key, token, body)
    return Response(status_code=201)
