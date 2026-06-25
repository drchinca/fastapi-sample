from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_tool_registry
from app.schemas.tools import ToolCallRequest, ToolCallResponse, ToolDescriptor
from app.tools.registry import ToolInputError, ToolNotFoundError, ToolRegistry

router = APIRouter(prefix="/tools", tags=["tools"])

Registry = Annotated[ToolRegistry, Depends(get_tool_registry)]


@router.get("", response_model=list[ToolDescriptor])
def list_tools(registry: Registry) -> list[ToolDescriptor]:
    """List every registered tool with its JSON Schema — MCP-style discovery."""
    return [tool.descriptor() for tool in registry.list()]


@router.post("/run", response_model=ToolCallResponse)
def run_tool(payload: ToolCallRequest, registry: Registry) -> ToolCallResponse:
    """Dispatch a tool by name; arguments are validated against the tool's input model."""
    try:
        tool = registry.get(payload.tool)
    except ToolNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown tool '{payload.tool}'",
        ) from exc

    try:
        result = tool.invoke(payload.arguments)
    except ToolInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ToolCallResponse(tool=tool.name, result=result)
