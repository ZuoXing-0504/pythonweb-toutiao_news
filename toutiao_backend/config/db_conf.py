from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from config.settings import get_settings

settings = get_settings()
# 创建异步引擎
async_engine = create_async_engine(
 settings.database_url,
 echo=settings.debug_mode,
 pool_size=settings.database_pool_size,
 max_overflow=settings.database_max_overflow,
)
# 创建异步会话⼯⼚
AsyncSessionLocal = async_sessionmaker(
 bind=async_engine,
 class_=AsyncSession,
 expire_on_commit=False
)
# 依赖项，⽤于获取数据库会话
async def get_db():
   async with AsyncSessionLocal() as session:
    try:
     yield session
     await session.commit()
    except Exception:
     await session.rollback()
     raise
    finally:
     await session.close()
