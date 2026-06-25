from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

router = APIRouter(tags=["dev"])
_basic = HTTPBasic(auto_error=False)


class Ping(BaseModel):
    message: str = "ping"


@router.post("/marketo-test")
def marketo_test(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(_basic)],
) -> dict[str, str]:
    name = credentials.username if credentials else "guest"
    return {"message": f"hello {name}"}


@router.get("/marketo-key")
def marketo_key_get() -> dict[str, str]:
    return {"message": "pong"}


@router.post("/marketo-key")
def marketo_key_post(body: Ping) -> dict[str, str]:
    return {"message": "pong" if body.message.lower() == "ping" else "ping"}
