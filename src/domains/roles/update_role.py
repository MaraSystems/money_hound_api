from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.roles.get_role import get_role
from src.domains.roles.model import Role, UpdateRole
from src.domains.users.model import User
from src.lib.utils.response import DataResponse


async def update_role(id: ObjectId, payload: UpdateRole, db: Database, cache: Redis) -> DataResponse[Role]:
    role_collection = db.roles
    role = await get_role(id, db, cache)

    if payload.title:
        existing = await role_collection.find_one({'title': payload.title, '_id': {'$ne': id}})
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Role title not available: {payload.title}')

    await role_collection.update_one({'_id': id}, {'$set': payload.model_dump(exclude_unset=True)})
    
    await cache.delete(f'role:{id}')
    await cache.delete(f'role:{role.data.title}')

    updated_role = await get_role(id, db, cache)

    return DataResponse(data=updated_role.data, message='Role updated successfully')