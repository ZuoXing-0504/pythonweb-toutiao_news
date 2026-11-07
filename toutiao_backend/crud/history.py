from sqlalchemy.ext.asyncio import AsyncSession
from models.news import News
from models.history import History
from models.base import utc_now
from sqlalchemy import select,func,delete
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert


#添加历史记录
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    view_time = utc_now()
    values = {
        "user_id": user_id,
        "news_id": news_id,
        "view_time": view_time,
    }
    dialect_name = db.get_bind().dialect.name

    if dialect_name == "mysql":
        insert_stmt = mysql_insert(History).values(**values)
        stmt = insert_stmt.on_duplicate_key_update(view_time=view_time)
    elif dialect_name == "sqlite":
        insert_stmt = sqlite_insert(History).values(**values)
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[History.user_id, History.news_id],
            set_={"view_time": view_time},
        )
    else:
        raise RuntimeError(f"不支持的数据库类型: {dialect_name}")

    await db.execute(stmt)
    result = await db.execute(
        select(History).where(
            History.user_id == user_id,
            History.news_id == news_id,
        )
    )
    return result.scalar_one()

#获取浏览历史列表
async def list_history(
        db: AsyncSession,
        user_id: int,
        page:int = 1,
        page_size:int = 10
):
    query = select(func.count(History.id)).where(History.user_id == user_id)
    result = await db.execute(query)
    total = result.scalar()

    has_more = total > (page * page_size)
    query = select(
        News,
        History.id.label("history_id"),
        History.view_time.label("view_time")
    ).join(
        History,
        News.id == History.news_id
    ).where(
        History.user_id == user_id
    ).order_by(
        History.view_time.desc()
    ).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(query)
    history_list = result.all()
    return history_list,total,has_more

#删除单条历史记录
async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = delete(History).where(History.news_id == news_id, History.user_id == user_id)
    result = await db.execute(query)
    return result.rowcount > 0
#清空浏览历史列表
async def clear_history(
        db: AsyncSession,
        user_id: int
):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    return result.rowcount or 0
