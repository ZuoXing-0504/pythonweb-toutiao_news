from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import (
    get_cached_categories,
    get_cached_news_page,
    set_cached_categories,
    set_cached_news_page,
)
from models.news import Category, News
from schemas.base import CategoryResponse, NewsItemBase, NewsListResponse


async def get_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[CategoryResponse]:
    cached = await get_cached_categories(skip, limit)
    if cached is not None:
        return [CategoryResponse.model_validate(item) for item in cached]

    stmt = (
        select(Category)
        .order_by(Category.sort_order, Category.id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    categories = [CategoryResponse.model_validate(item) for item in result.scalars().all()]
    payload = [item.model_dump(mode="json") for item in categories]
    await set_cached_categories(skip, limit, payload)
    return categories


async def get_news_page(
    db: AsyncSession,
    category_id: int,
    page: int = 1,
    page_size: int = 10,
) -> NewsListResponse:
    cached = await get_cached_news_page(category_id, page, page_size)
    if cached is not None:
        return NewsListResponse.model_validate(cached)

    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .order_by(News.publish_time.desc(), News.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    news_items = [NewsItemBase.model_validate(item) for item in result.scalars().all()]
    total = await db.scalar(
        select(func.count(News.id)).where(News.category_id == category_id)
    )
    page_data = NewsListResponse(
        list=news_items,
        total=total or 0,
        has_more=(page * page_size) < (total or 0),
    )
    await set_cached_news_page(
        category_id,
        page,
        page_size,
        page_data.model_dump(mode="json"),
    )
    return page_data
