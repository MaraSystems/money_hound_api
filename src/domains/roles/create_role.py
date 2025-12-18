from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.roles.model import CreateRole, Role
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def create_role(payload: CreateRole, author_id: str, db: Database, cache: Redis) -> DataResponse[Role]:
    role_collection = db.roles
    existing = await lazyload(cache, f'role:{payload.title}', loader=role_collection.find_one, params={'filter': {'title': payload.title, 'hidden': False}})

    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Role title not available: {payload.title}')

    insert = await role_collection.insert_one({**payload.model_dump(), 'author_id': author_id})
    role = await role_collection.find_one({'_id': insert.inserted_id})

    return DataResponse(data=Role(**role), message=f'Role created successfully: {payload.title}')
