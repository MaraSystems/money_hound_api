from fastapi import status, HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulation_bank_devices.model import SimulationBankDevice
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_simulation_bank_device(id: ObjectId, db: Database, cache: Redis):
    simulation_bank_device_collection = db.simulation_bank_devices
    bank_device = await lazyload(cache, f'simulation_bank_device:{id}', loader=simulation_bank_device_collection.find_one, params={'_id': id})

    if not bank_device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Simulation Bank Device not found: {str(id)}')

    return DataResponse[SimulationBankDevice](data=bank_device)