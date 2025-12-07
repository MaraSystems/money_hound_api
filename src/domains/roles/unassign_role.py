from fastapi import HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.roles.get_role import get_role
from src.domains.users.get_user import get_user

from ...lib.utils.response import DataResponse


async def unassign_role(id: ObjectId, user_id: ObjectId, db: Database, cache: Redis):
    role = await get_role(id, db, cache)
    await get_user(user_id, db, cache)
    
    role_collection = db.roles
    await role_collection.update_one(
        {"_id": id},
        {"$pull": {"users": str(user_id)}},
    )

    await cache.delete(f'role:{id}')
    await cache.delete(f'role:{role.data.title}')

    return DataResponse(message="Role unassigned from user successfully")