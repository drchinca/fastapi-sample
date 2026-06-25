import json
import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from auth import require_basic_auth
from users import random_email, random_name

router = APIRouter(tags=["ssfs"])

SERVICE_DEFINITION: dict[str, Any] = {
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


def _load_openapi() -> dict[str, Any]:
    spec = json.loads((Path(__file__).resolve().parent / "openapi.json").read_text())
    if base_url := os.getenv("API_BASE_URL", "").strip():
        spec["servers"] = [{"url": base_url.rstrip("/")}]
    elif domain := os.getenv("REPLIT_DEV_DOMAIN", "").strip():
        spec["servers"] = [{"url": f"https://{domain}"}]
    return spec


@router.get("/install")
def install() -> JSONResponse:
    return JSONResponse(_load_openapi())


@router.get("/getServiceDefinition", dependencies=[Depends(require_basic_auth)])
def get_service_definition() -> dict[str, Any]:
    return SERVICE_DEFINITION


@router.get("/status", dependencies=[Depends(require_basic_auth)])
def status() -> dict[str, list[str]]:
    return {"info": ["Random User POC is running."]}


@router.post(
    "/submitAsyncAction",
    status_code=201,
    dependencies=[Depends(require_basic_auth)],
)
def submit_async_action(payload: dict[str, Any]) -> Response:
    callback_objects: list[dict[str, Any]] = []

    for item in payload.get("objectData", []):
        lead_id = item.get("objectContext", {}).get("id")
        callback_objects.append(
            {
                "leadData": {"id": lead_id},
                "activityData": {
                    "generated_email": random_email(),
                    "generated_name": random_name(),
                    "success": True,
                },
            }
        )

    munchkin_id = payload.get("context", {}).get("subscription", {}).get("munchkinId", "")
    callback_body = {"munchkinId": munchkin_id, "objectData": callback_objects}

    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            payload["callbackUrl"],
            headers={
                "x-api-key": payload["apiCallBackKey"],
                "x-callback-token": payload["token"],
                "Content-Type": "application/json",
            },
            json=callback_body,
        )

    if response.is_success:
        return Response(status_code=201)

    return JSONResponse(
        status_code=500,
        content={"error": response.text},
    )
