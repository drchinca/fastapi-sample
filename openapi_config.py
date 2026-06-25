import os
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

OPENAPI_VERSION = "3.0.3"

MARKETO_SECURITY_SCHEMES: dict[str, Any] = {
    "apiKey": {
        "type": "apiKey",
        "name": "x-api-key",
        "in": "header",
        "description": "API key header used by Marketo to authenticate with this service.",
    }
}

MARKETO_SECURITY: list[dict[str, list[str]]] = [{"apiKey": []}]


def get_server_url() -> str:
    if base_url := os.getenv("API_BASE_URL", "").strip():
        return base_url.rstrip("/")
    if domain := os.getenv("REPLIT_DEV_DOMAIN", "").strip():
        return f"https://{domain}"
    return "http://127.0.0.1:8000"


def build_marketo_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["openapi"] = OPENAPI_VERSION
    openapi_schema["servers"] = [
        {
            "url": get_server_url(),
            "description": "Deployed service base URL",
        }
    ]

    components = openapi_schema.setdefault("components", {})
    components["securitySchemes"] = MARKETO_SECURITY_SCHEMES
    openapi_schema["security"] = MARKETO_SECURITY

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "responses" in operation:
                operation["security"] = MARKETO_SECURITY

    app.openapi_schema = openapi_schema
    return openapi_schema


def validate_marketo_openapi(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not str(schema.get("openapi", "")).startswith("3.0"):
        errors.append("openapi version must be 3.0.x for Marketo compatibility")

    if not schema.get("security"):
        errors.append("missing root-level security")

    security_schemes = schema.get("components", {}).get("securitySchemes", {})
    if "apiKey" not in security_schemes:
        errors.append("missing components.securitySchemes.apiKey")

    api_key_scheme = security_schemes.get("apiKey", {})
    if api_key_scheme.get("type") != "apiKey":
        errors.append("apiKey scheme must use type apiKey")
    if api_key_scheme.get("in") not in {"header", "query"}:
        errors.append("apiKey scheme must declare in: header or query")
    if not api_key_scheme.get("name"):
        errors.append("apiKey scheme must declare name")

    if not schema.get("servers"):
        errors.append("missing servers")
    else:
        for server in schema["servers"]:
            if not server.get("url"):
                errors.append("servers entry missing url")

    if not schema.get("paths"):
        errors.append("missing paths")

    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.startswith("x-"):
                continue
            if not isinstance(operation, dict):
                continue
            if "security" not in operation:
                errors.append(f"missing operation security: {method.upper()} {path}")
            if not operation.get("responses"):
                errors.append(f"missing responses: {method.upper()} {path}")
            else:
                for status, response in operation["responses"].items():
                    if not response.get("description"):
                        errors.append(
                            f"missing response description: {method.upper()} {path} {status}"
                        )

    return errors
