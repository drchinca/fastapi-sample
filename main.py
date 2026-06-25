from typing import Any

from fastapi import Depends, FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

from endpoints import cars, users

bearer_auth = HTTPBearer(
    scheme_name="bearerAuth",
    description="Bearer token for Adobe Marketo POC integrations.",
    auto_error=False,
)

app = FastAPI(
    title="FastAPI Sample",
    summary="Minimal FastAPI app with CRUD on /cars and random users on /users.",
    version="0.2.0",
    dependencies=[Depends(bearer_auth)],
)

app.include_router(cars.router)
app.include_router(users.router)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})[
        "bearerAuth"
    ] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Bearer token for Adobe Marketo POC integrations.",
    }
    openapi_schema["security"] = [{"bearerAuth": []}]

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "responses" in operation:
                operation["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"message": "hello andres"}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
