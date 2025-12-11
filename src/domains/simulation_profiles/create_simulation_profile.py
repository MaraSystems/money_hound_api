from pymongo.database import Database
from redis.asyncio import Redis
from fastapi import HTTPException, status

from src.domains.simulation_profiles.model import CreateSimulationProfile, SimulationProfile
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def create_simulation_profile(payload: CreateSimulationProfile, db: Database, cache: Redis) -> DataResponse[SimulationProfile]:
    simulation_profile_collection = db.simulation_profiles
    existing = await lazyload(cache, f'simulation_profile:{payload.email}', loader=simulation_profile_collection.find_one, params={'email': payload.email, 'simulation_id': payload.simulation_id})

    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Simulation Email not available: {payload.email}')

    insert = await simulation_profile_collection.insert_one(payload.model_dump())
    profile = await simulation_profile_collection.find_one({'_id': insert.inserted_id})

    return DataResponse(data=SimulationProfile(**profile), message='Simulation Profile created successfully')
