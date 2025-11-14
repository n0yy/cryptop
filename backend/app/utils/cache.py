import json
from typing import Any, Optional
import redis.asyncio as redis
from app.config import settings
from app.utils.logger import logger

redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    try:
        client = await get_redis_client()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def cache_set(key: str, value: Any, ttl: int = None) -> bool:
    try:
        client = await get_redis_client()
        ttl = ttl or settings.REDIS_CACHE_TTL
        await client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


async def cache_delete(key: str) -> bool:
    try:
        client = await get_redis_client()
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False


async def cache_exists(key: str) -> bool:
    try:
        client = await get_redis_client()
        return await client.exists(key) > 0
    except Exception as e:
        logger.error(f"Cache exists error: {e}")
        return False
