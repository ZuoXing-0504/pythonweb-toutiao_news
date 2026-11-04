from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from cache.news_cache import get_cached_categories, set_cached_categories,get_cached_news_list,set_cached_news_list
from schemas.base import NewsItemBase


async def get_categories(db:AsyncSession, skip: int = 0, limit: int = 100):
    #查缓存是否有数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories
    stmt = select(Category).order_by(Category.sort_order, Category.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    #将查询结果写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)
    return categories

# 新闻列表
async def get_news_list(db:AsyncSession,category_id: int,  skip: int = 0, limit: int = 10):
    #查缓存是否有数据
    page = skip // limit + 1
    cached_news = await get_cached_news_list(category_id,page,limit)
    if cached_news:
        return [News(**news) for news in cached_news]
    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .order_by(News.publish_time.desc(), News.id.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    news = result.scalars().all()
    #将查询结果写入缓存
    if news:
        #orm->pydantic->dict
        news = [NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news]
        await set_cached_news_list(category_id,page,limit,news)
    return news
#新闻指定分类总量
async def get_news_total(db:AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    total = result.scalar_one()
    return total
#新闻详情
async def get_news_detail(db:AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()
    return news
# 新闻增加浏览量
async def increase_news_views(db:AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    #检查数据库是否命中了数据-命中了return true
    return result.rowcount > 0
#相关新闻
async def get_related_news(db:AsyncSession, category_id: int, news_id: int,limit: int = 5):
    #查询分类下的其他新闻
    #排除当前新闻
    #按浏览量和发布时间排序
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
        ).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return [{
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time,
            "categoryId": news.category_id,
            "views": news.views,
    } for news in related_news]
