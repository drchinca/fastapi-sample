from typing import Any

from pydantic import BaseModel, Field


class EchoArgs(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class AddArgs(BaseModel):
    a: float
    b: float


class ToolCall(BaseModel):
    """Dispatch envelope: tool name + arguments object."""

    tool: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolDescriptor(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


class ToolResult(BaseModel):
    tool: str
    result: Any
