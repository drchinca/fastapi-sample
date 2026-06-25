from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=60)
    email: str = Field(min_length=3, max_length=120)
