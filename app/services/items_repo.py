from itertools import count
from threading import Lock

from app.schemas.items import Item, ItemCreate, ItemPatch, ItemUpdate


class ItemNotFoundError(KeyError):
    """Raised when an item id is not present in the repository."""


class ItemsRepository:
    """Thread-safe in-memory CRUD store. Swap for a DB-backed implementation later."""

    def __init__(self) -> None:
        self._items: dict[int, Item] = {}
        self._ids = count(1)
        self._lock = Lock()

    def list(self) -> list[Item]:
        with self._lock:
            return list(self._items.values())

    def get(self, item_id: int) -> Item:
        with self._lock:
            try:
                return self._items[item_id]
            except KeyError as exc:
                raise ItemNotFoundError(item_id) from exc

    def create(self, payload: ItemCreate) -> Item:
        with self._lock:
            item = Item(id=next(self._ids), **payload.model_dump())
            self._items[item.id] = item
            return item

    def replace(self, item_id: int, payload: ItemUpdate) -> Item:
        with self._lock:
            if item_id not in self._items:
                raise ItemNotFoundError(item_id)
            item = Item(id=item_id, **payload.model_dump())
            self._items[item_id] = item
            return item

    def patch(self, item_id: int, payload: ItemPatch) -> Item:
        with self._lock:
            try:
                existing = self._items[item_id]
            except KeyError as exc:
                raise ItemNotFoundError(item_id) from exc
            updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
            self._items[item_id] = updated
            return updated

    def delete(self, item_id: int) -> None:
        with self._lock:
            if self._items.pop(item_id, None) is None:
                raise ItemNotFoundError(item_id)
