from fastapi import APIRouter, Query

from schemas.users import User
from utils.users import random_email, random_name

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[User])
def list_users(
    count: int = Query(default=10, ge=1, le=100, description="How many users to return"),
) -> list[User]:
    return [User(id=i, name=random_name(), email=random_email()) for i in range(1, count + 1)]
