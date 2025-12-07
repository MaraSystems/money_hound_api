import json
from typing import List

from langchain_core.messages import AnyMessage
from redis.asyncio import Redis


async def update_chat_session(cache: Redis, session_id, messages: List[dict]):
    data = json.dumps(messages)
    await cache.set(f'chat:{session_id}', data)


async def get_chat_session(cache: Redis, session_id: str) -> List[AnyMessage]:
    data = await cache.get(f'chat:{session_id}')
    return json.loads(data) if data else []
    