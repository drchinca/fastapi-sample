from typing import Any

from fastapi import Depends, FastAPI

from auth import require_marketo_auth
from endpoints import cars, users
from openapi_config import build_marketo_openapi

app = FastAPI(
    title="FastAPI Sample",
    summary="Minimal FastAPI app with CRUD on /cars and random users on /users.",
    description=(
        "Adobe Marketo POC service exposing user and car endpoints. "
        "OpenAPI supports Basic auth or x-api-key authentication."
    ),
    version="0.4.0",
)

app.include_router(cars.router, dependencies=[Depends(require_marketo_auth)])
app.include_router(users.router, dependencies=[Depends(require_marketo_auth)])


def custom_openapi() -> dict[str, Any]:
    return build_marketo_openapi(app)


app.openapi = custom_openapi


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"message": "hello andres"}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
