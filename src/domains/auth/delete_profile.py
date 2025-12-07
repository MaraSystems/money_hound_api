from bson import ObjectId
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.auth.get_profile import get_profile

from ...lib.utils.response import DataResponse


async def delete_profile(user_id: ObjectId, db: Database, cache: Redis):
    user_collection = db.users
    profile = await get_profile(user_id, db, cache)

    await user_collection.update_one({'_id': user_id}, {'$set': {'hidden': True}})

    await cache.delete(f'user:{user_id}')
    await cache.delete(f'user:{profile.data.email}')

    return DataResponse(message='Profile deleted successfully')
