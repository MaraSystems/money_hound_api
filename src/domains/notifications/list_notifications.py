from datetime import datetime
from bson import ObjectId
from pymongo.database import Database

from src.lib.utils.pagination import sort_mapping
from .model import ListNotifications, Notification
from src.lib.utils.response import DataResponse


async def list_notification(payload: ListNotifications, user_id: str, db: Database) -> DataResponse[list[Notification]]:
    notification_collection = db.notifications
    query = {
        '$and': [
            {
                '$or': [
                    {'public': True},
                    {'users': user_id}
                ]
            },
            {
                '$or': [
                    {'expires_at': None},
                    {'expires_at': {'$gt': datetime.now()}}
                ]
            }
        ]
    }
    if payload.query is not None:
        query = {
            **query,
            **{
                '$or': [
                    {'subject': {'$regex': f'^{payload.query}', "$options": "i"}}
                ]
            }
        }

    data = (await notification_collection.find(query)
                 .sort('created_at', sort_mapping[payload.sort])
                 .limit(payload.limit)
                 .skip(payload.skip)
                 .to_list())
    
    return DataResponse(data=data)
