from pydantic import BaseModel, Field


class CarIn(BaseModel):
    color: str = Field(min_length=1, max_length=30)
    model: str = Field(min_length=1, max_length=60)


class CarPatch(BaseModel):
    color: str | None = Field(default=None, min_length=1, max_length=30)
    model: str | None = Field(default=None, min_length=1, max_length=60)


class Car(CarIn):
    id: int
