from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from models.news import News
from models.history import History
from sqlalchemy import select,func,delete


#添加历史记录
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query =select(History).where(History.news_id == news_id, History.user_id == user_id).limit(1)
    result = await db.execute(query)
    history = result.scalar()

    if history:
        history.view_time = datetime.now()
        await db.commit()
        await db.refresh(history)
        return history
    else:
        history = History(user_id=user_id,news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

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
    query = select(History).where(History.news_id == news_id, History.user_id == user_id)
    result = await db.execute(query)
    history = result.scalar()
    if history:
        await db.delete(history)
        await db.commit()
        return history
    else:
        return None
#清空浏览历史列表
async def clear_history(
        db: AsyncSession,
        user_id: int
):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount
