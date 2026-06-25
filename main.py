from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from dev.routes import router as dev_router
from endpoints import cars, users
from ssfs.routes import router as ssfs_router

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

app = FastAPI(
    title="FastAPI Sample",
    summary="Cars CRUD, random users, and a Marketo SSFS flow action.",
    version="1.0.0",
)

app.include_router(cars.router)
app.include_router(users.router)
app.include_router(ssfs_router)
app.include_router(dev_router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"message": "hello andres"}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "docs": "/docs",
        "openapi": "/openapi.json",
        "marketo_install": "/install",
    }
