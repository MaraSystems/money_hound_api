import json

from redis.asyncio import Redis


async def start_conversation(session_id: str, user_id: str, cache: Redis):
    """Initialize a new conversation session in cache if it doesn't exist

    Args:
        session_id: Unique identifier for the conversation session
        user_id: ID of the user initiating the conversation
        cache: Redis cache connection
    """
    data = await cache.get(f'conversations:{session_id}')
    if data == None:
        data = json.dumps({'user_id': user_id, 'history': []})
        await cache.set(f'conversations:{session_id}', data)
