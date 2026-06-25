from fastapi import FastAPI

from endpoints import cars, users

app = FastAPI(
    title="FastAPI Sample",
    summary="Minimal FastAPI app with CRUD on /cars and random users on /users.",
)

app.include_router(cars.router)
app.include_router(users.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"message": "hello andres"}


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
