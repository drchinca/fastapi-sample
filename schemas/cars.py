from pydantic import BaseModel, Field


class CarIn(BaseModel):
    """Payload for creating or replacing a car."""

    color: str = Field(min_length=1, max_length=30)
    model: str = Field(min_length=1, max_length=60)


class CarPatch(BaseModel):
    """Partial update payload — every field optional."""

    color: str | None = Field(default=None, min_length=1, max_length=30)
    model: str | None = Field(default=None, min_length=1, max_length=60)


class Car(CarIn):
    """A car as returned by the API."""

    id: int
