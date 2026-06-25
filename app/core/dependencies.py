from functools import lru_cache

from app.services.items_repo import ItemsRepository
from app.tools.registry import ToolRegistry, build_default_registry


@lru_cache
def get_items_repo() -> ItemsRepository:
    """Singleton repository — override in tests via `app.dependency_overrides`."""
    return ItemsRepository()


@lru_cache
def get_tool_registry() -> ToolRegistry:
    return build_default_registry()
