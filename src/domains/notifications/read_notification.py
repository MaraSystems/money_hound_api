from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.notifications.get_notification import get_notification
from src.domains.users.get_user import get_user
from src.lib.utils.response import DataResponse


async def read_notification(id: ObjectId, user_id: str, db: Database, cache: Redis):
    notification_collection = db.notifications
    await get_notification(id, db, cache, user_id)

    await notification_collection.find_one_and_update(
        {'_id': id}, 
        {"$addToSet": {"readers": str(user_id)}}
    )
    
    await cache.delete(f'notification:{id}')
    return DataResponse(message='User read notification successfully')