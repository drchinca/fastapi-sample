from typing import Any

from fastapi import Depends, FastAPI
from fastapi.security import APIKeyHeader

from endpoints import cars, users
from openapi_config import build_marketo_openapi

api_key_auth = APIKeyHeader(
    name="x-api-key",
    scheme_name="apiKey",
    description="API key header used by Marketo to authenticate with this service.",
    auto_error=False,
)

app = FastAPI(
    title="FastAPI Sample",
    summary="Minimal FastAPI app with CRUD on /cars and random users on /users.",
    description=(
        "Adobe Marketo POC service exposing user and car endpoints. "
        "OpenAPI is configured for Marketo import with apiKey security."
    ),
    version="0.3.0",
    dependencies=[Depends(api_key_auth)],
)

app.include_router(cars.router)
app.include_router(users.router)


def custom_openapi() -> dict[str, Any]:
    return build_marketo_openapi(app)


app.openapi = custom_openapi


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"message": "hello andres"}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
