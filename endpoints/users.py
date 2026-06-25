import random
import string

from fastapi import APIRouter, Query

from schemas.users import User

router = APIRouter(prefix="/users", tags=["users"])

_FIRST_NAMES = ("Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery")
_LAST_NAMES = ("Smith", "Lee", "Patel", "Garcia", "Kim", "Nguyen", "Brown", "Davis")


def _random_email() -> str:
    local = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 14)))
    domain = "".join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
    tld = random.choice(("com", "org", "net", "io", "dev"))
    return f"{local}@{domain}.{tld}"


def _random_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


@router.get("", response_model=list[User])
def list_users(
    count: int = Query(default=10, ge=1, le=100, description="Number of users to return"),
) -> list[User]:
    return [
        User(id=i, name=_random_name(), email=_random_email())
        for i in range(1, count + 1)
    ]
