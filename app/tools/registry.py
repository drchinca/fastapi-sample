from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from app.schemas.tools import ToolDescriptor


class ToolNotFoundError(KeyError):
    """Raised when a tool name is not registered."""


class ToolInputError(ValueError):
    """Raised when a tool's arguments fail schema validation."""


@dataclass(frozen=True, slots=True)
class Tool:
    """A registered tool: name + description + typed input model + handler."""

    name: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[[BaseModel], Any]

    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            name=self.name,
            description=self.description,
            input_schema=self.input_model.model_json_schema(),
        )

    def invoke(self, raw_arguments: dict[str, Any]) -> Any:
        try:
            parsed = self.input_model.model_validate(raw_arguments)
        except ValidationError as exc:
            raise ToolInputError(str(exc)) from exc
        return self.handler(parsed)


class ToolRegistry:
    """Name-indexed collection of tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(name) from exc

    def list(self) -> list[Tool]:
        return list(self._tools.values())


def build_default_registry() -> ToolRegistry:
    from app.tools.add import add_tool
    from app.tools.echo import echo_tool

    registry = ToolRegistry()
    registry.register(echo_tool)
    registry.register(add_tool)
    return registry
