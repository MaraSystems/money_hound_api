from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.notifications.model import Notification
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_notification(id: ObjectId, db: Database, cache: Redis, user_id: str = None) -> DataResponse[Notification]:
    notification_collection = db.notifications
    notification = await lazyload(cache, f'notification:{id}', loader=notification_collection.find_one, params={'_id': id})

    if notification is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'Notification not found: {id}')

    if user_id and not notification['public'] and user_id not in notification['users']:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=f'You are unauthorized to read this notification: {id}')

    return DataResponse(data=Notification(**notification))