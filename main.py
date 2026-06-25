from itertools import count
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="FastAPI Sample",
    summary="Two endpoint groups: full CRUD on /cars and an MCP-style tool dispatcher on /tools.",
)


# ---------- /cars : full CRUD over an in-memory store ---------- #


class CarIn(BaseModel):
    color: str = Field(min_length=1, max_length=30)
    model: str = Field(min_length=1, max_length=60)


class CarPatch(BaseModel):
    color: str | None = Field(default=None, min_length=1, max_length=30)
    model: str | None = Field(default=None, min_length=1, max_length=60)


class Car(CarIn):
    id: int


_cars: dict[int, Car] = {}
_car_ids = count(1)


def _get_car(car_id: int) -> Car:
    car = _cars.get(car_id)
    if car is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Car {car_id} not found")
    return car


@app.get("/cars", response_model=list[Car], tags=["cars"])
def list_cars() -> list[Car]:
    return list(_cars.values())


@app.post("/cars", response_model=Car, status_code=status.HTTP_201_CREATED, tags=["cars"])
def create_car(payload: CarIn) -> Car:
    car = Car(id=next(_car_ids), **payload.model_dump())
    _cars[car.id] = car
    return car


@app.get("/cars/{car_id}", response_model=Car, tags=["cars"])
def get_car(car_id: int) -> Car:
    return _get_car(car_id)


@app.put("/cars/{car_id}", response_model=Car, tags=["cars"])
def replace_car(car_id: int, payload: CarIn) -> Car:
    _get_car(car_id)
    car = Car(id=car_id, **payload.model_dump())
    _cars[car_id] = car
    return car


@app.patch("/cars/{car_id}", response_model=Car, tags=["cars"])
def patch_car(car_id: int, payload: CarPatch) -> Car:
    car = _get_car(car_id)
    updated = car.model_copy(update=payload.model_dump(exclude_unset=True))
    _cars[car_id] = updated
    return updated


@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["cars"])
def delete_car(car_id: int) -> None:
    _get_car(car_id)
    del _cars[car_id]


# ---------- /tools : MCP-style dispatcher ---------- #


class EchoArgs(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class AddArgs(BaseModel):
    a: float
    b: float


_TOOLS: dict[str, tuple[str, type[BaseModel], Any]] = {
    "echo": (
        "Return the input message verbatim.",
        EchoArgs,
        lambda args: {"echoed": args.message},
    ),
    "add": (
        "Return the sum of two numbers.",
        AddArgs,
        lambda args: {"sum": args.a + args.b},
    ),
}


class ToolCall(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


@app.get("/tools", tags=["tools"])
def list_tools() -> list[dict[str, Any]]:
    return [
        {"name": name, "description": desc, "input_schema": model.model_json_schema()}
        for name, (desc, model, _) in _TOOLS.items()
    ]


@app.post("/tools/run", tags=["tools"])
def run_tool(call: ToolCall) -> dict[str, Any]:
    entry = _TOOLS.get(call.tool)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown tool '{call.tool}'")
    _, input_model, handler = entry
    args = input_model.model_validate(call.arguments)
    return {"tool": call.tool, "result": handler(args)}


# ---------- root ---------- #


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"docs": "/docs", "openapi": "/openapi.json"}
