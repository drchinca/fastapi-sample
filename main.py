from fastapi import FastAPI

from routers import cars, tools

app = FastAPI(
    title="FastAPI Sample",
    summary="Two endpoint groups: full CRUD on /cars and an MCP-style tool dispatcher on /tools.",
)

app.include_router(cars.router)
app.include_router(tools.router)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
