"""Redis-backed rate limit helpers."""

from redis.asyncio import Redis


class RateLimiter:
    """Simple fixed-window asynchronous rate limiter."""

    def __init__(self, redis: Redis, namespace: str) -> None:
        self._redis = redis
        self._namespace = namespace

    async def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        """Return whether a key is allowed under the given rate limit."""
        redis_key = f"rate:{self._namespace}:{key}"
        count = await self._redis.incr(redis_key)
        if count == 1:
            await self._redis.expire(redis_key, window_seconds)
        return int(count) <= limit
