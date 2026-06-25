from pydantic import BaseModel

from app.tools.registry import Tool


class AddInput(BaseModel):
    """Arguments for the `add` tool."""

    a: float
    b: float


class AddOutput(BaseModel):
    sum: float


def _add(payload: AddInput) -> AddOutput:
    return AddOutput(sum=payload.a + payload.b)


add_tool = Tool(
    name="add",
    description="Return the sum of two numbers.",
    input_model=AddInput,
    handler=_add,
)
