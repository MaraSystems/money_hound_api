from fastapi import APIRouter, Depends, Query, Request
from typing import Annotated
from bson import ObjectId
from typing import List

from src.config.cache import get_cache
from src.middlewares.role_guard import require_permission


from ...config.database import get_db
from .create_role import create_role
from .delete_role import delete_role
from .update_role import update_role
from .get_role import get_role
from .list_domains import list_domains
from .list_roles import list_roles as fetch_roles
from .unassign_role import unassign_role
from .assign_role import assign_role

from .model import CreateRole, Domain, ListRoles, Role, UpdateRole
from ...lib.utils.response import DataResponse
from ...middlewares.auth_guard import get_current_user

role_router = APIRouter(prefix='/roles')


@role_router.get(
    '/domains', 
    response_model=DataResponse[List[Domain]], 
    name="List Role Domains"
)
async def fetch_domains(
    permissons=Depends(require_permission('roles:domains:read'))
) -> DataResponse[List[Domain]]: 
    return await list_domains()


@role_router.post(
    '', 
    response_model=DataResponse[Role], 
    name="Create Role", status_code=201
)
async def create(
    role: CreateRole, 
    user=Depends(get_current_user), 
    db=Depends(get_db),
    cache=Depends(get_cache),
    permissons=Depends(require_permission('roles:base:write'))
) -> DataResponse[Role]:
    return await create_role(role, user.id, db, cache)


@role_router.get(
    '/{id}', 
    response_model=DataResponse[Role], 
    name="Get Role"
)
async def get(
    id: str, 
    db=Depends(get_db),
    cache=Depends(get_cache),
    permissons=Depends(require_permission('roles:base:read'))
) -> DataResponse[Role]:
    return await get_role(ObjectId(id), db, cache)


@role_router.patch(
    '/{id}', 
    response_model=DataResponse[Role], 
    name="Update Role"
)
async def update(
    id: str, 
    payload: UpdateRole, 
    db=Depends(get_db),
    cache=Depends(get_cache),
    permissons=Depends(require_permission('roles:base:write'))
) -> DataResponse[Role]:
    return await update_role(ObjectId(id), payload, db, cache)


@role_router.get(
    '',
    response_model=DataResponse[List[Role]],
    name="List Roles"
)
async def list_roles(
    payload: Annotated[Query, Depends(ListRoles)],
    db=Depends(get_db),
    permissons=Depends(require_permission('roles:base:read'))
) -> DataResponse[List[Role]]:
    return await fetch_roles(payload, db)


@role_router.delete(
    '/{id}',
    response_model=DataResponse[None],
    name="Delete Role"
)
async def delete(
    id: str,
    db=Depends(get_db),
    cache=Depends(get_cache),
    permissons=Depends(require_permission('roles:base:write'))
) -> DataResponse[None]:
    return await delete_role(ObjectId(id), db, cache)


@role_router.post(
    '/{id}/assign/{user_id}',
    response_model=DataResponse[None],
    name="Assign Role"
)
async def assign(
    id: str,
    user_id: str,
    db=Depends(get_db),
    cache=Depends(get_cache),
    permissons=Depends(require_permission('roles:users:write'))
) -> DataResponse[None]:
    return await assign_role(ObjectId(id), ObjectId(user_id), db, cache)


@role_router.delete(
    '/{id}/unassign/{user_id}',
    response_model=DataResponse[None],
    name="Unassign Role"
)
async def unassign(
    id: str, 
    user_id: str, 
    db=Depends(get_db),
    cache=Depends(get_cache),
    permissons=Depends(require_permission('roles:users:write'))
) -> DataResponse[None]:
    return await unassign_role(ObjectId(id), ObjectId(user_id), db, cache)
