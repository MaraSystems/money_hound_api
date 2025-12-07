from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.notifications.get_notification import get_notification
from src.domains.users.get_user import get_user
from src.lib.utils.response import DataResponse


async def notify_user(id: ObjectId, user_id: str, db: Database, cache: Redis):
    notification_collection = db.notifications
    
    notification = await get_notification(id, db, cache)
    if notification.data.public:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f'Notification is already public: {id}')
    
    await notification_collection.find_one_and_update(
        {'_id': id}, 
        {"$addToSet": {"users": user_id}}
    )

    await cache.delete(f'notification:{id}')

    return DataResponse(message='User notified successfully')