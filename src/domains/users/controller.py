from bson import ObjectId
from fastapi import APIRouter, Depends, Query
from typing import List, Annotated

from src.db.cache import get_cache
from src.domains.users.get_user import get_user
from src.domains.users.list_users import list_users
from src.middlewares.role_guard import require_permission

from ...middlewares.auth_guard import get_current_user
from ...models.response import DataResponse, PageResponse
from ...db.database import get_db
from ...models.user import User, ListUsers

user_router = APIRouter(prefix='/users')


@user_router.get('', response_model=PageResponse[User])
async def fetch(
    page: Annotated[Query, Depends(ListUsers)], 
    db=Depends(get_db),
    user=Depends(get_current_user),
    permissons=Depends(require_permission('users:base:read'))
) -> PageResponse[User]:
    return await list_users(page, db)


@user_router.get('/{id}', response_model=DataResponse[User])
async def get(
    id: str, 
    db=Depends(get_db), 
    cache=Depends(get_cache),
    user=Depends(get_current_user),
    permissons=Depends(require_permission('users:base:read'))
):
    return await get_user(ObjectId(id), db, cache)