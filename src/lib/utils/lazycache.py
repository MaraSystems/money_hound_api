from datetime import datetime
from bson import ObjectId
import json
from typing import Any, Callable, Awaitable

from redis.asyncio import Redis

from src.config.config import CACHE_TTL

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o) 
        if isinstance(o, datetime):
            return o.isoformat() 
        return super().default(o)


async def lazyload(cache: Redis, key: str, loader: Callable[[Any], Awaitable[Any]], params: Any, expiry: int = CACHE_TTL,):
    value = await cache.get(key)
    if value is not None:
        return json.loads(value)

    result = await loader(**params)
    if result is not None:
        value = json.dumps(result, cls=EnhancedJSONEncoder)
        await cache.set(key, value, ex=expiry)

    return result
