import redis.asyncio as redis
import json
from typing import Any
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

#设置 和 读取缓存
#读取缓存：字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"读取缓存失败：{e}")
        return None

#读取缓存：列表 或 字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"读取缓存失败：{e}")
        return None
#设置缓存
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        await redis_client.set(key, value=value, ex=expire)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False
