import os
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials

basic_auth = HTTPBasic(
    scheme_name="basic",
    description="HTTP Basic auth using MARKETO_USER and MARKETO_PASSWORD.",
    auto_error=False,
)

api_key_auth = APIKeyHeader(
    name="x-api-key",
    scheme_name="apiKey",
    description="API key header using MARKETO_API_KEY.",
    auto_error=False,
)


def _credentials_configured() -> bool:
    return bool(
        os.getenv("MARKETO_USER")
        and os.getenv("MARKETO_PASSWORD")
    ) or bool(os.getenv("MARKETO_API_KEY"))


def _valid_basic(credentials: HTTPBasicCredentials | None) -> bool:
    if credentials is None:
        return False

    expected_user = os.getenv("MARKETO_USER", "")
    expected_password = os.getenv("MARKETO_PASSWORD", "")
    if not expected_user or not expected_password:
        return False

    return secrets.compare_digest(credentials.username, expected_user) and secrets.compare_digest(
        credentials.password, expected_password
    )


def _valid_api_key(api_key: str | None) -> bool:
    if not api_key:
        return False

    expected_key = os.getenv("MARKETO_API_KEY", "")
    if not expected_key:
        return False

    return secrets.compare_digest(api_key, expected_key)


def require_marketo_auth(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_auth)],
    api_key: Annotated[str | None, Depends(api_key_auth)],
) -> None:
    if not _credentials_configured():
        return

    if _valid_basic(credentials) or _valid_api_key(api_key):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": 'Basic realm="FastAPI Sample"'},
    )
