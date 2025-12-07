from typing import Annotated, List
from bson import ObjectId
from fastapi import Depends, Query
from fastapi.routing import APIRouter

from src.config.cache import get_cache
from src.config.database import get_db
from src.domains.auth.model import CurrentUser
from src.domains.notifications.create_notification import create_notification
from src.domains.notifications.get_notification import get_notification
from src.domains.notifications.list_notifications import list_notification
from src.domains.notifications.model import CreateNotification, ListNotifications, Notification
from src.domains.notifications.read_notification import read_notification
from src.lib.utils.response import DataResponse
from src.middlewares.auth_guard import get_current_user
from src.middlewares.role_guard import require_permission

notification_router = APIRouter(prefix='/notifications')


@notification_router.post(
    '',
    response_model=DataResponse[Notification],
    name="Create Notification",
    status_code=201
)
async def create(
    payload: CreateNotification,
    db=Depends(get_db),
    user: CurrentUser =Depends(get_current_user),
    permissons=Depends(require_permission('notifications:base:write'))
) -> DataResponse[Notification]:
    return await create_notification(payload, db)


@notification_router.get(
    '',
    response_model=DataResponse[List[Notification]],
    name="List Notifications"
)
async def fetch(
    payload: Annotated[Query, Depends(ListNotifications)],
    db=Depends(get_db),
    user: CurrentUser =Depends(get_current_user)
) -> DataResponse[List[Notification]]:
    return await list_notification(payload, user.id, db)


@notification_router.get(
    '/{id}', 
    name='Get Notification'
)
async def get(
    id: str,
    user: CurrentUser=Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache)
) -> DataResponse[Notification]:
    return await get_notification(ObjectId(id), db, cache, user_id=user.id)


@notification_router.put(
    '/{id}', 
    name='Read Notification'
)
async def read(
    id: str,
    db=Depends(get_db),
    cache=Depends(get_cache),
    user: CurrentUser =Depends(get_current_user)
) -> DataResponse[None]:
    return await read_notification(ObjectId(id), user.id, db, cache)