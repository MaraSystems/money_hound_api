from datetime import datetime
from pymongo.database import Database

from src.models.pagination import sort_mapping
from src.models.notification import ListNotifications, Notification
from src.models.response import PageResponse


async def list_notification(payload: ListNotifications, user_id: str, db: Database) -> PageResponse[Notification]:
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
        .limit(payload.limit+1)
        .skip(payload.skip * payload.limit)
        .to_list())
    
    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)