import json
import logging
from typing import Any

import redis.asyncio as redis
from redis.exceptions import RedisError

from config.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=settings.redis_timeout_seconds,
    socket_timeout=settings.redis_timeout_seconds,
)


async def get_json_cache(key: str) -> Any | None:
    try:
        data = await redis_client.get(key)
        return json.loads(data) if data is not None else None
    except (RedisError, json.JSONDecodeError) as exc:
        logger.warning("Redis cache read failed for key %s: %s", key, exc)
        return None


async def set_json_cache(key: str, value: Any, expire: int = 3600) -> bool:
    try:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        await redis_client.set(key, value=payload, ex=expire)
        return True
    except (RedisError, TypeError, ValueError) as exc:
        logger.warning("Redis cache write failed for key %s: %s", key, exc)
        return False
