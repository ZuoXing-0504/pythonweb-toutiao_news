from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite


# 检查该用户是否收藏了该新闻
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
) -> bool:
    stmt = select(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    return result.scalar() is not None






