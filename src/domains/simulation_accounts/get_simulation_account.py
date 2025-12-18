from fastapi import status, HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulation_accounts.model import SimulationAccount
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_simulation_account(id: ObjectId, db: Database, cache: Redis):
    simulation_account_collection = db.simulation_accounts
    account = await lazyload(cache, f'simulation_account:{id}', loader=simulation_account_collection.find_one, params={'filter': {'_id': id}})

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Simulation Account not found: {str(id)}')

    return DataResponse[SimulationAccount](data=account)