from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.simulations.get_simulation import get_simulation
from src.domains.simulations.model import Simulation, UpdateSimulation
from src.lib.utils.response import DataResponse
from src.tasks.simulations import simulator


async def update_simulation(id: ObjectId, payload: UpdateSimulation, user_id: str, db: Database, cache: Redis) -> DataResponse[Simulation]:
    simulation_collection = db.simulations
    simulation = await get_simulation(id, db, cache)

    if simulation.data.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'You are not authorized')

    await simulation_collection.update_one({'_id': id}, {'$set': payload.model_dump(exclude_unset=True)})
    
    await cache.delete(f'simulation:{id}')

    updated = await get_simulation(id, db, cache)
    updated_data = updated.data.model_dump(exclude=['id'])
    updated_data['_id'] = updated.data.id
    simulator.delay(updated_data, user_id)
    return DataResponse[Simulation](data=updated.data, message='Simulation re-initiated successfully')