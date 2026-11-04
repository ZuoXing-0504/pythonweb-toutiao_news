import json
import logging
import os
from typing import Any

import redis.asyncio as redis
from dotenv import load_dotenv
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_TIMEOUT_SECONDS = float(os.getenv("REDIS_TIMEOUT_SECONDS", "1.0"))

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=REDIS_TIMEOUT_SECONDS,
    socket_timeout=REDIS_TIMEOUT_SECONDS,
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
