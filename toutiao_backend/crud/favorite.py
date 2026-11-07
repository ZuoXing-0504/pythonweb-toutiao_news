from sqlalchemy import select,delete,func
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from models.news import News


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
    values = {"user_id": user_id, "news_id": news_id}
    dialect_name = db.get_bind().dialect.name

    if dialect_name == "mysql":
        insert_stmt = mysql_insert(Favorite).values(**values)
        stmt = insert_stmt.on_duplicate_key_update(
            news_id=insert_stmt.inserted.news_id
        )
    elif dialect_name == "sqlite":
        insert_stmt = sqlite_insert(Favorite).values(**values)
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[Favorite.user_id, Favorite.news_id],
            set_={"news_id": insert_stmt.excluded.news_id},
        )
    else:
        raise RuntimeError(f"不支持的数据库类型: {dialect_name}")

    await db.execute(stmt)
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id,
        )
    )
    return result.scalar_one()

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
    return result.rowcount > 0

# 获取收藏列表,连表查询新闻信息
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
) :
    count_query =select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    #连表分页查询+收藏时间排序
    stmt = (select(News,Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))
            .join(Favorite,Favorite.news_id == News.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            )
    result = await db.execute(stmt)
    return result.all(),total

#清空收藏列表
async def clear_favorite(
        db: AsyncSession,
        user_id: int
) -> int:
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result =await db.execute(stmt)
    return result.rowcount or 0





