import os
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

basic = HTTPBasic(auto_error=False)


def require_marketo_basic(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic)],
) -> None:
    """Optional until MARKETO_USER and MARKETO_PASSWORD are both set."""
    user = os.getenv("MARKETO_USER", "").strip()
    password = os.getenv("MARKETO_PASSWORD", "").strip()
    if not user or not password:
        return
    if credentials and secrets.compare_digest(credentials.username, user) and secrets.compare_digest(
        credentials.password, password
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": 'Basic realm="FastAPI Sample"'},
    )
