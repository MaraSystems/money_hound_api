from fastapi import status, HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.models.simulation_devices import SimulationDevice
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_simulation_device(id: ObjectId, db: Database, cache: Redis):
    simulation_device_collection = db.simulation_devices
    device = await lazyload(cache, f'simulation_device:{id}', loader=simulation_device_collection.find_one, params={'_id': id})

    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Simulation Device not found: {str(id)}')

    return DataResponse[SimulationDevice](data=device)