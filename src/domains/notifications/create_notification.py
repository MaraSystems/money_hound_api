from pymongo.database import Database

from src.domains.notifications.model import CreateNotification
from src.lib.utils.response import DataResponse


async def create_notification(payload: CreateNotification, db: Database):
    notification_collection = db.notifications
    await notification_collection.insert_one(payload.model_dump())
    return DataResponse(message='Notification created successfully')