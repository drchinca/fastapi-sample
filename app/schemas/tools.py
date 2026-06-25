from typing import Any

from pydantic import BaseModel, Field


class ToolDescriptor(BaseModel):
    """Public, MCP-style description of a callable tool."""

    name: str
    description: str
    input_schema: dict[str, Any]


class ToolCallRequest(BaseModel):
    """Dispatch envelope: name the tool, pass its typed arguments."""

    tool: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    tool: str
    result: Any
