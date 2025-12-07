from fastapi import HTTPException, status
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.auth.get_profile import get_profile

from ...domains.auth.model import UpdateProfile
from ...domains.users.model import User
from ...lib.utils.response import DataResponse


async def update_profile(id: ObjectId, payload: UpdateProfile, db: Database, cache: Redis):
    user_collection = db.users
    user = await get_profile(id, db, cache)

    if payload.email:
        existing = await user_collection.find_one({'email': payload.email, 'hidden': False, '_id': {'$ne': id}})
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Email not available: {payload.email}')

    await user_collection.update_one({'_id': id}, {'$set': payload.model_dump(exclude_unset=True)})

    await cache.delete(f'user:{id}')
    await cache.delete(f'user:{user.data.email}')

    updated_user = await get_profile(id, db, cache)
    return DataResponse(data=updated_user.data, message='Profile updated successfully')
