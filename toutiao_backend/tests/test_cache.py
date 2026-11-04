from datetime import datetime
from unittest.mock import AsyncMock

from redis.exceptions import ConnectionError

from cache import news_cache as cache_keys
from config import cache_conf
from crud import news_cache
from models.news import Category, News


def cached_news_payload() -> dict:
    return {
        "id": 1,
        "title": "缓存新闻",
        "description": "缓存简介",
        "image": None,
        "author": "测试作者",
        "category_id": 1,
        "views": 8,
        "publish_time": "2026-11-04T12:00:00",
    }


async def test_news_cache_hit_skips_database(monkeypatch):
    get_cached = AsyncMock(return_value={
        "list": [cached_news_payload()],
        "total": 11,
        "has_more": True,
    })
    monkeypatch.setattr(news_cache, "get_cached_news_page", get_cached)
    db = AsyncMock()
    db.execute.side_effect = AssertionError("database should not be queried on a cache hit")
    db.scalar.side_effect = AssertionError("database should not be queried on a cache hit")

    result = await news_cache.get_news_page(db, category_id=1, page=1, page_size=10)

    assert result.list[0].title == "缓存新闻"
    assert isinstance(result.list[0].publish_time, datetime)
    assert result.total == 11
    assert result.has_more is True
    db.execute.assert_not_awaited()
    db.scalar.assert_not_awaited()
    get_cached.assert_awaited_once_with(1, 1, 10)


async def test_news_cache_miss_reads_database_and_writes_dto(
    session_factory, monkeypatch
):
    get_cached = AsyncMock(return_value=None)
    set_cached = AsyncMock(return_value=True)
    monkeypatch.setattr(news_cache, "get_cached_news_page", get_cached)
    monkeypatch.setattr(news_cache, "set_cached_news_page", set_cached)

    async with session_factory() as session:
        category = Category(name="国内", sort_order=1)
        session.add(category)
        await session.flush()
        session.add(
            News(
                title="数据库新闻",
                description="数据库简介",
                content="正文",
                author="测试作者",
                category_id=category.id,
                publish_time=datetime(2026, 11, 4, 12, 0, 0),
            )
        )
        await session.commit()

        result = await news_cache.get_news_page(
            session,
            category_id=category.id,
            page=1,
            page_size=10,
        )

    assert result.list[0].title == "数据库新闻"
    assert result.total == 1
    payload = set_cached.await_args.args[3]
    assert payload["list"][0]["title"] == "数据库新闻"
    assert payload["list"][0]["publish_time"] == "2026-11-04T12:00:00"
    assert payload["total"] == 1
    assert "_sa_instance_state" not in payload["list"][0]


async def test_empty_results_use_short_ttl(monkeypatch):
    set_json = AsyncMock(return_value=True)
    monkeypatch.setattr(cache_keys, "set_json_cache", set_json)

    empty_page = {"list": [], "total": 0, "has_more": False}
    await cache_keys.set_cached_news_page(1, 1, 10, empty_page)

    set_json.assert_awaited_once_with("news:v1:list:1:1:10", empty_page, 60)


async def test_cache_failure_degrades_to_miss(monkeypatch):
    redis_get = AsyncMock(side_effect=ConnectionError("redis unavailable"))
    monkeypatch.setattr(cache_conf.redis_client, "get", redis_get)

    assert await cache_conf.get_json_cache("news:v1:test") is None
