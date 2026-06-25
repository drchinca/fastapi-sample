import os
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

basic_auth = HTTPBasic(auto_error=False)


def require_basic_auth(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_auth)],
) -> None:
    user = os.getenv("MARKETO_USER", "")
    password = os.getenv("MARKETO_PASSWORD", "")
    if not user or not password:
        return

    if credentials is None:
        raise _unauthorized()

    if secrets.compare_digest(credentials.username, user) and secrets.compare_digest(
        credentials.password, password
    ):
        return

    raise _unauthorized()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": 'Basic realm="Random User POC"'},
    )
