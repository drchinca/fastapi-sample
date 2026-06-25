from typing import Any

import httpx
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from dependencies.auth import require_basic_auth
from ssfs.openapi_loader import load_openapi
from utils.users import random_email, random_name

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


@router.get("/install")
def install() -> JSONResponse:
    return JSONResponse(load_openapi())


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
    callback_url = payload.get("callbackUrl")
    callback_key = payload.get("apiCallBackKey")
    token = payload.get("token")
    if not callback_url or not callback_key or not token:
        return JSONResponse(
            status_code=400,
            content={"error": "callbackUrl, apiCallBackKey, and token are required"},
        )

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

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                callback_url,
                headers={
                    "x-api-key": callback_key,
                    "x-callback-token": token,
                    "Content-Type": "application/json",
                },
                json=callback_body,
            )
    except httpx.HTTPError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})

    if response.is_success:
        return Response(status_code=201)

    return JSONResponse(
        status_code=500,
        content={"error": response.text},
    )
