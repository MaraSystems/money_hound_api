from typing import Any


from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.roles.get_role import get_role
from src.domains.simulations.get_simulation import get_simulation

from ...lib.utils.response import DataResponse


async def delete_simulation(id: ObjectId, user_id: str, db: Database, cache: Redis):
    simulation_collection = db.simulations
    simulation = await get_simulation(id, db, cache)

    if simulation.data.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'You are not authorized')
        
    await simulation_collection.update_one({'_id': id}, {'$set': {'hidden': True}})
    
    await cache.delete(f'simulation:{id}')

    return DataResponse(message='Simulation deleted successfully')
