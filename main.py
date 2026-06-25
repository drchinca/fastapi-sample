from fastapi import FastAPI

from endpoints import cars

app = FastAPI(
    title="FastAPI Sample",
    summary="Minimal FastAPI app with full CRUD on /cars.",
)

app.include_router(cars.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"message": "hello andres"}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
