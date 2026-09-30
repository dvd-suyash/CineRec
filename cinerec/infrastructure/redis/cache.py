import json
import asyncio
from typing import Optional, Any, Callable, TypeVar, Awaitable
from redis.asyncio import Redis, from_url
from cinerec.core.config import settings

T = TypeVar('T')

class RedisCache:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.client = from_url(redis_url, decode_responses=True)
        
    async def get(self, key: str) -> Optional[Any]:
        data = await self.client.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self.client.set(key, value, ex=ttl_seconds)
        
    async def get_or_set(
        self, 
        key: str, 
        fetcher: Callable[[], Awaitable[T]], 
        ttl_seconds: int = 3600,
        lock_timeout: int = 10,
        retry_delay: float = 0.5,
        max_retries: int = 5
    ) -> Optional[T]:
        """
        Cache-aside pattern with stampede prevention (mutex lock).
        """
        # Try getting from cache first
        cached = await self.get(key)
        if cached is not None:
            return cached
            
        lock_key = f"lock:{key}"
        
        # Try to acquire the lock to prevent cache stampede
        for attempt in range(max_retries):
            # NX = Set if not exists, EX = expire lock after timeout
            acquired = await self.client.set(lock_key, "locked", nx=True, ex=lock_timeout)
            
            if acquired:
                try:
                    # Double-check cache in case another worker just filled it
                    cached = await self.get(key)
                    if cached is not None:
                        return cached
                        
                    # Fetch fresh data
                    fresh_data = await fetcher()
                    if fresh_data is not None:
                        await self.set(key, fresh_data, ttl_seconds)
                    return fresh_data
                finally:
                    # Release lock
                    await self.client.delete(lock_key)
            else:
                # Wait and retry if someone else is fetching
                await asyncio.sleep(retry_delay)
                cached = await self.get(key)
                if cached is not None:
                    return cached
                    
        # If we exhausted retries and couldn't get lock or cache, try fetching anyway as last resort
        # or return None. We'll fetch as last resort but not cache it to avoid trampling.
        return await fetcher()

    async def close(self):
        await self.client.close()

# Global redis cache instance
redis_cache = RedisCache()
