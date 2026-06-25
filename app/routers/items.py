from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.dependencies import get_items_repo
from app.schemas.items import Item, ItemCreate, ItemPatch, ItemUpdate
from app.services.items_repo import ItemNotFoundError, ItemsRepository

router = APIRouter(prefix="/items", tags=["items"])

Repo = Annotated[ItemsRepository, Depends(get_items_repo)]


@router.get("", response_model=list[Item])
def list_items(repo: Repo) -> list[Item]:
    return repo.list()


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, repo: Repo) -> Item:
    return repo.create(payload)


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, repo: Repo) -> Item:
    try:
        return repo.get(item_id)
    except ItemNotFoundError as exc:
        raise _not_found(item_id) from exc


@router.put("/{item_id}", response_model=Item)
def replace_item(item_id: int, payload: ItemUpdate, repo: Repo) -> Item:
    try:
        return repo.replace(item_id, payload)
    except ItemNotFoundError as exc:
        raise _not_found(item_id) from exc


@router.patch("/{item_id}", response_model=Item)
def patch_item(item_id: int, payload: ItemPatch, repo: Repo) -> Item:
    try:
        return repo.patch(item_id, payload)
    except ItemNotFoundError as exc:
        raise _not_found(item_id) from exc


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, repo: Repo) -> Response:
    try:
        repo.delete(item_id)
    except ItemNotFoundError as exc:
        raise _not_found(item_id) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _not_found(item_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item {item_id} not found",
    )
