from fastapi import status, HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.roles.model import Role
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_role(id: ObjectId, db: Database, cache: Redis):
    role_collection = db.roles
    role = await lazyload(cache, f'role:{id}', loader=role_collection.find_one, params={'filter': {'_id': id, 'hidden': False}})

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Role not found: {str(id)}')

    return DataResponse(data=Role(**role))