from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from models.history import History
from sqlalchemy import select


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

