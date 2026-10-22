import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

load_dotenv()

# 数据库URL
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
if not ASYNC_DATABASE_URL:
    raise RuntimeError("缺少 ASYNC_DATABASE_URL 环境变量，请参考 .env.example 配置")
# 创建异步引擎
async_engine = create_async_engine(
 ASYNC_DATABASE_URL,
 echo=True, # 可选：输出SQL⽇志
 pool_size=10, # 设置连接池中保持的持久连接数
 max_overflow=20 # 设置连接池允许创建的额外连接数
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
