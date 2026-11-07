import asyncio
import os
from uuid import uuid4

import pytest
import pytest_asyncio
import redis.asyncio as redis
from redis.exceptions import RedisError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import cache_conf
from crud import favorite, history, users
from models.favorite import Favorite
from models.history import History
from models.news import Category, News
from models.users import User, UserToken


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def mysql_session_factory():
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not configured")

    engine = create_async_engine(database_url, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def real_redis(monkeypatch):
    redis_url = os.getenv("TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("TEST_REDIS_URL is not configured")

    client = redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=1.0,
        socket_timeout=1.0,
    )
    for _ in range(20):
        try:
            await client.ping()
            break
        except RedisError:
            await asyncio.sleep(0.5)
    else:
        await client.aclose()
        pytest.fail("Redis did not become ready within 10 seconds")

    await client.flushdb()
    monkeypatch.setattr(cache_conf, "redis_client", client)
    yield client
    await client.flushdb()
    await client.aclose()


async def run_together(factory, operation, count: int = 6):
    start = asyncio.Event()

    async def worker():
        async with factory() as session:
            await start.wait()
            result = await operation(session)
            await session.commit()
            return result

    tasks = [asyncio.create_task(worker()) for _ in range(count)]
    await asyncio.sleep(0)
    start.set()
    return await asyncio.gather(*tasks)


async def test_mysql_concurrent_upserts(mysql_session_factory):
    suffix = uuid4().hex[:12]
    async with mysql_session_factory() as session:
        user = User(username=f"integration_{suffix}", password="unused_hash")
        category = Category(name=f"integration_{suffix}", sort_order=1)
        session.add_all([user, category])
        await session.flush()
        news = News(
            title="MySQL integration test",
            content="test",
            category_id=category.id,
        )
        session.add(news)
        await session.commit()
        user_id, news_id = user.id, news.id

    favorite_rows = await run_together(
        mysql_session_factory,
        lambda session: favorite.add_favorite(session, user_id, news_id),
    )
    history_rows = await run_together(
        mysql_session_factory,
        lambda session: history.add_history(session, user_id, news_id),
    )
    issued_tokens = await run_together(
        mysql_session_factory,
        lambda session: users.create_token(session, user_id),
    )

    async with mysql_session_factory() as session:
        favorite_count = await session.scalar(
            select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        )
        history_count = await session.scalar(
            select(func.count(History.id)).where(History.user_id == user_id)
        )
        token_rows = (
            await session.scalars(
                select(UserToken).where(UserToken.user_id == user_id)
            )
        ).all()

    assert favorite_count == 1
    assert history_count == 1
    assert len({row.id for row in favorite_rows}) == 1
    assert len({row.id for row in history_rows}) == 1
    assert len(token_rows) == 1
    assert token_rows[0].token in issued_tokens


async def test_redis_json_round_trip_and_expiry(real_redis):
    key = f"integration:{uuid4().hex}"
    payload = {"title": "缓存测试", "items": [1, 2, 3]}

    assert await cache_conf.set_json_cache(key, payload, expire=30) is True
    assert await cache_conf.get_json_cache(key) == payload
    ttl = await real_redis.ttl(key)
    assert 0 < ttl <= 30
