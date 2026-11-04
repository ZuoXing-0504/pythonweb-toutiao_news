from typing import Any

from config.cache_conf import get_json_cache, set_json_cache


CACHE_VERSION = "v1"
CATEGORIES_KEY = f"news:{CACHE_VERSION}:categories"
NEWS_LIST_KEY = f"news:{CACHE_VERSION}:list"


def categories_cache_key(skip: int, limit: int) -> str:
    return f"{CATEGORIES_KEY}:{skip}:{limit}"


def news_list_cache_key(category_id: int, page: int, size: int) -> str:
    return f"{NEWS_LIST_KEY}:{category_id}:{page}:{size}"


async def get_cached_categories(skip: int, limit: int) -> list[dict[str, Any]] | None:
    return await get_json_cache(categories_cache_key(skip, limit))


async def set_cached_categories(
    skip: int,
    limit: int,
    data: list[dict[str, Any]],
    expire: int = 7200,
) -> bool:
    ttl = expire if data else 60
    return await set_json_cache(categories_cache_key(skip, limit), data, ttl)


async def get_cached_news_page(
    category_id: int,
    page: int,
    size: int,
) -> dict[str, Any] | None:
    return await get_json_cache(news_list_cache_key(category_id, page, size))


async def set_cached_news_page(
    category_id: int,
    page: int,
    size: int,
    data: dict[str, Any],
    expire: int = 600,
) -> bool:
    ttl = expire if data.get("list") else 60
    return await set_json_cache(news_list_cache_key(category_id, page, size), data, ttl)
