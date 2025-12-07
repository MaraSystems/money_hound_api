from redis import asyncio
from redis.asyncio import Redis

from .config import REDIS_URL

redis_client: Redis = None

def get_cache():
    global redis_client
    redis_client = asyncio.from_url(f'{REDIS_URL}/0', decode_responses=True)
    return redis_client