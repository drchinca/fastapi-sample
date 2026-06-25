from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    """Payload for creating a new item."""

    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    description: str | None = None


class ItemUpdate(BaseModel):
    """Full replacement payload for PUT."""

    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    description: str | None = None


class ItemPatch(BaseModel):
    """Partial update payload for PATCH — every field optional."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0)
    description: str | None = None


class Item(BaseModel):
    """Item as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    description: str | None = None
