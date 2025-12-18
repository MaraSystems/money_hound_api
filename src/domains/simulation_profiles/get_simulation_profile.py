from fastapi import status, HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulation_profiles.model import SimulationProfile
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_simulation_profile(id: ObjectId, db: Database, cache: Redis):
    simulation_profile_collection = db.simulation_profiles
    profile = await lazyload(cache, f'simulation_profile:{id}', loader=simulation_profile_collection.find_one, params={'filter': {'_id': id}})

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Simulation Profile not found: {str(id)}')

    return DataResponse[SimulationProfile](data=profile)