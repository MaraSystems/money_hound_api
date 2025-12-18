from fastapi import HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.lib.utils.lazycache import lazyload
from ...domains.users.model import User
from ...lib.utils.response import DataResponse


async def get_profile(user_id: ObjectId, db: Database, cache: Redis):
    user_collection = db.users
    profile = await lazyload(cache, f'user:{user_id}', loader=user_collection.find_one, params={'filter': {'_id': user_id, 'hidden': False}})

    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {user_id}")

    return DataResponse(data=User(**profile))
