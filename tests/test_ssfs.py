"""SSFS endpoint tests — auth, sync ack + async callback delivery."""

import base64

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response

from main import app

MARKETO_USER = "marketo"
MARKETO_PASSWORD = "secret"
CALLBACK_URL = "https://app-sjqe.marketo.com/rest/v1/leads/ssfs/callback"
CALLBACK_KEY = "ABC123-callback-key"
CALLBACK_TOKEN = "one-time-callback-token"
MUNCHKIN_ID = "123-ABC-456"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Client with Marketo Basic auth credentials configured."""
    monkeypatch.setenv("MARKETO_USER", MARKETO_USER)
    monkeypatch.setenv("MARKETO_PASSWORD", MARKETO_PASSWORD)
    return TestClient(app)


@pytest.fixture
def open_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Client with auth disabled (no credentials set)."""
    monkeypatch.delenv("MARKETO_USER", raising=False)
    monkeypatch.delenv("MARKETO_PASSWORD", raising=False)
    return TestClient(app)


def _basic_header(user: str, password: str) -> dict[str, str]:
    raw = f"{user}:{password}".encode()
    return {"Authorization": f"Basic {base64.b64encode(raw).decode()}"}


def _invocation_payload(callback_url: str = CALLBACK_URL) -> dict:
    return {
        "callbackUrl": callback_url,
        "apiCallBackKey": CALLBACK_KEY,
        "token": CALLBACK_TOKEN,
        "context": {"subscription": {"munchkinId": MUNCHKIN_ID}},
        "flowAttributes": [{"apiName": "label", "value": "demo"}],
        "objectData": [
            {"objectContext": {"id": 1001}, "leadData": {"email": "alice@example.com"}},
            {"objectContext": {"id": 1002}, "leadData": {"email": "bob@example.com"}},
        ],
    }


# ── /install ──────────────────────────────────────────────────────────────────


def test_install_returns_openapi_without_auth(client: TestClient) -> None:
    response = client.get("/install")
    assert response.status_code == 200
    spec = response.json()
    assert spec["openapi"].startswith("3.")
    assert "/submitAsyncAction" in spec["paths"]


def test_install_rewrites_server_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_BASE_URL", "https://my-public-host.example.com/")
    response = TestClient(app).get("/install")
    assert response.json()["servers"] == [{"url": "https://my-public-host.example.com"}]


# ── auth ──────────────────────────────────────────────────────────────────────


def test_get_service_definition_requires_auth(client: TestClient) -> None:
    assert client.get("/getServiceDefinition").status_code == 401


def test_get_service_definition_rejects_wrong_password(client: TestClient) -> None:
    response = client.get(
        "/getServiceDefinition",
        headers=_basic_header(MARKETO_USER, "wrong"),
    )
    assert response.status_code == 401


def test_get_service_definition_accepts_valid_basic_auth(client: TestClient) -> None:
    response = client.get(
        "/getServiceDefinition",
        headers=_basic_header(MARKETO_USER, MARKETO_PASSWORD),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["apiName"] == "random-user-poc"
    assert {"generated_email", "generated_name"} == {
        attr["apiName"] for attr in body["callbackPayloadDef"]["attributes"]
    }


def test_auth_is_bypassed_when_credentials_not_configured(open_client: TestClient) -> None:
    """Default-open until MARKETO_USER + MARKETO_PASSWORD are set."""
    assert open_client.get("/getServiceDefinition").status_code == 200
    assert open_client.get("/status").status_code == 200


def test_status_requires_auth_when_configured(client: TestClient) -> None:
    assert client.get("/status").status_code == 401
    response = client.get("/status", headers=_basic_header(MARKETO_USER, MARKETO_PASSWORD))
    assert response.status_code == 200
    assert response.json() == {"info": ["Random User POC is running."]}


# ── /submitAsyncAction — validation ──────────────────────────────────────────


def test_submit_async_action_requires_auth(client: TestClient) -> None:
    assert client.post("/submitAsyncAction", json=_invocation_payload()).status_code == 401


@pytest.mark.parametrize("missing", ["callbackUrl", "apiCallBackKey", "token"])
def test_submit_async_action_400_when_required_field_missing(
    client: TestClient, missing: str
) -> None:
    payload = _invocation_payload()
    payload.pop(missing)
    response = client.post(
        "/submitAsyncAction",
        json=payload,
        headers=_basic_header(MARKETO_USER, MARKETO_PASSWORD),
    )
    assert response.status_code == 400
    assert "required" in response.json()["error"]


# ── /submitAsyncAction — async ack + callback delivery ───────────────────────


@respx.mock
def test_submit_async_action_acks_201_and_delivers_callback(client: TestClient) -> None:
    callback_route = respx.post(CALLBACK_URL).mock(return_value=Response(200))

    response = client.post(
        "/submitAsyncAction",
        json=_invocation_payload(),
        headers=_basic_header(MARKETO_USER, MARKETO_PASSWORD),
    )

    assert response.status_code == 201
    assert callback_route.called, "background callback was not delivered"

    sent = callback_route.calls.last.request
    assert sent.headers["x-api-key"] == CALLBACK_KEY
    assert sent.headers["x-callback-token"] == CALLBACK_TOKEN
    assert sent.headers["content-type"] == "application/json"

    import json as _json
    body = _json.loads(sent.content)
    assert body["munchkinId"] == MUNCHKIN_ID
    assert [item["leadData"]["id"] for item in body["objectData"]] == [1001, 1002]
    for item in body["objectData"]:
        activity = item["activityData"]
        assert activity["success"] is True
        assert "@" in activity["generated_email"]
        assert activity["generated_name"]


@respx.mock
def test_submit_async_action_still_acks_201_when_callback_fails(client: TestClient) -> None:
    """SSFS spec: provider MUST return 201 regardless of downstream callback outcome."""
    respx.post(CALLBACK_URL).mock(return_value=Response(500, text="marketo unavailable"))

    response = client.post(
        "/submitAsyncAction",
        json=_invocation_payload(),
        headers=_basic_header(MARKETO_USER, MARKETO_PASSWORD),
    )

    assert response.status_code == 201
    assert response.content == b""


@respx.mock
def test_submit_async_action_still_acks_201_when_callback_unreachable(client: TestClient) -> None:
    import httpx

    respx.post(CALLBACK_URL).mock(side_effect=httpx.ConnectError("DNS fail"))

    response = client.post(
        "/submitAsyncAction",
        json=_invocation_payload(),
        headers=_basic_header(MARKETO_USER, MARKETO_PASSWORD),
    )

    assert response.status_code == 201
