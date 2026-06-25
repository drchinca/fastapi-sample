from fastapi import FastAPI

from app.routers import items, tools

app = FastAPI(
    title="FastAPI Sample",
    version="0.1.0",
    summary="A minimal Pythonic FastAPI app: one CRUD resource and one MCP-style tool dispatcher.",
)

app.include_router(items.router)
app.include_router(tools.router)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
