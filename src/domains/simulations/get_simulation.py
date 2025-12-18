from fastapi import status, HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulations.model import Simulation
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_simulation(id: ObjectId, db: Database, cache: Redis):
    simulation_collection = db.simulations
    simulation = await lazyload(cache, f'simulation:{id}', loader=simulation_collection.find_one, params={'filter': {'_id': id, 'hidden': False}})

    if not simulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Simulation not found: {str(id)}')

    return DataResponse(data=Simulation(**simulation))