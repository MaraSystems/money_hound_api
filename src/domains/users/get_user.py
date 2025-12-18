from bson import ObjectId
from pymongo.database import Database
from fastapi import HTTPException
from redis.asyncio import Redis

from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse

async def get_user(id: ObjectId, db: Database, cache: Redis):
    user_collection = db.users
    user = await lazyload(cache, f'user:{id}', loader=user_collection.find_one, params={'filter': {'_id': id, 'hidden': False}})

    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {id}")

    return DataResponse(data=user)