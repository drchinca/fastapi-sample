from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ValidationError

from schemas.tools import AddArgs, EchoArgs, ToolCall, ToolDescriptor, ToolResult

router = APIRouter(prefix="/tools", tags=["tools"])


def _echo(args: EchoArgs) -> dict[str, str]:
    return {"echoed": args.message}


def _add(args: AddArgs) -> dict[str, float]:
    return {"sum": args.a + args.b}


_TOOLS: dict[str, tuple[str, type[BaseModel], Callable[[Any], Any]]] = {
    "echo": ("Return the input message verbatim.", EchoArgs, _echo),
    "add": ("Return the sum of two numbers.", AddArgs, _add),
}


@router.get("", response_model=list[ToolDescriptor])
def list_tools() -> list[ToolDescriptor]:
    """List every registered tool with its JSON Schema — MCP-style discovery."""
    return [
        ToolDescriptor(name=name, description=desc, input_schema=model.model_json_schema())
        for name, (desc, model, _) in _TOOLS.items()
    ]


@router.post("/run", response_model=ToolResult)
def run_tool(call: ToolCall) -> ToolResult:
    """Dispatch a tool by name; arguments are validated against the tool's input model."""
    entry = _TOOLS.get(call.tool)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown tool '{call.tool}'")
    _, input_model, handler = entry
    try:
        args = input_model.model_validate(call.arguments)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors()) from exc
    return ToolResult(tool=call.tool, result=handler(args))
