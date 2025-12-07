from bson import ObjectId
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.roles.get_role import get_role

from ...lib.utils.response import DataResponse


async def delete_role(id: ObjectId, db: Database, cache: Redis):
    role_collection = db.roles
    role = await get_role(id, db, cache)
    await role_collection.update_one({'_id': id}, {'$set': {'hidden': True}})
    
    await cache.delete(f'role:{id}')
    await cache.delete(f'role:{role.data.title}')

    return DataResponse(message='Role deleted successfully')
