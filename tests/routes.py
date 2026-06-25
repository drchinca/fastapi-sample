from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

router = APIRouter(tags=["tests"])
basic_auth = HTTPBasic(auto_error=False)


class PingBody(BaseModel):
    message: str = "ping"


def _hello_name(credentials: HTTPBasicCredentials | None) -> str:
    return credentials.username if credentials else "guest"


@router.post("/marketo-test")
def marketo_test(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_auth)],
) -> dict[str, str]:
    return {"message": f"hello {_hello_name(credentials)}"}


@router.get("/marketo-key")
def marketo_key_get() -> dict[str, str]:
    return {"message": "pong"}


@router.post("/marketo-key")
def marketo_key_post(body: PingBody) -> dict[str, str]:
    if body.message.lower() == "ping":
        return {"message": "pong"}
    return {"message": "ping"}
