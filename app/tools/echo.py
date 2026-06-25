from pydantic import BaseModel, Field

from app.tools.registry import Tool


class EchoInput(BaseModel):
    """Arguments for the `echo` tool."""

    message: str = Field(min_length=1, max_length=1000)


class EchoOutput(BaseModel):
    echoed: str


def _echo(payload: EchoInput) -> EchoOutput:
    return EchoOutput(echoed=payload.message)


echo_tool = Tool(
    name="echo",
    description="Return the input message verbatim. Useful as a connectivity check.",
    input_model=EchoInput,
    handler=_echo,
)
