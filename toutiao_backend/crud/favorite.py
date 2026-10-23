from sqlalchemy import select,delete
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

# 添加收藏
async def add_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
) -> Favorite:
    favorite = Favorite(
        user_id=user_id,
        news_id=news_id
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 取消收藏
async def remove_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
) :
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result =await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0




