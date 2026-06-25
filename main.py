from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI

from ssfs.openapi_loader import load_openapi
from ssfs.routes import router as ssfs_router
from tests.routes import router as tests_router

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

app = FastAPI(title="Random User POC", version="1.0.0")
app.include_router(ssfs_router)
app.include_router(tests_router)


def ssfs_openapi() -> dict[str, Any]:
    return load_openapi()


app.openapi = ssfs_openapi
