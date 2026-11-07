import asyncio

import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from crud import favorite, history, users
from models import Base
from models.favorite import Favorite
from models.history import History
from models.news import Category, News
from models.users import User, UserToken


@pytest_asyncio.fixture
async def concurrent_session_factory(tmp_path):
    database_path = tmp_path / "concurrency.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{database_path.as_posix()}",
        connect_args={"timeout": 30},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


async def seed_user_and_news(session_factory) -> tuple[int, int]:
    async with session_factory() as session:
        user = User(username="concurrent_user", password="unused_hash")
        category = Category(name="并发测试", sort_order=1)
        session.add_all([user, category])
        await session.flush()
        news = News(
            title="并发测试新闻",
            content="测试内容",
            category_id=category.id,
        )
        session.add(news)
        await session.commit()
        return user.id, news.id


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


async def test_concurrent_favorite_add_is_idempotent(concurrent_session_factory):
    user_id, news_id = await seed_user_and_news(concurrent_session_factory)

    records = await run_together(
        concurrent_session_factory,
        lambda session: favorite.add_favorite(session, user_id, news_id),
    )

    assert len({record.id for record in records}) == 1
    async with concurrent_session_factory() as session:
        count = await session.scalar(select(func.count(Favorite.id)))
        assert count == 1


async def test_concurrent_history_add_is_an_upsert(concurrent_session_factory):
    user_id, news_id = await seed_user_and_news(concurrent_session_factory)

    records = await run_together(
        concurrent_session_factory,
        lambda session: history.add_history(session, user_id, news_id),
    )

    assert len({record.id for record in records}) == 1
    async with concurrent_session_factory() as session:
        count = await session.scalar(select(func.count(History.id)))
        assert count == 1


async def test_concurrent_token_creation_keeps_one_row(concurrent_session_factory):
    user_id, _ = await seed_user_and_news(concurrent_session_factory)

    issued_tokens = await run_together(
        concurrent_session_factory,
        lambda session: users.create_token(session, user_id),
    )

    async with concurrent_session_factory() as session:
        tokens = (await session.scalars(select(UserToken))).all()
        assert len(tokens) == 1
        assert tokens[0].token in issued_tokens
