from fastapi import status, HTTPException
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulation_transactions.hound_transaction import hound_transaction
from src.domains.simulation_transactions.model import AnalyzedSimulationTransaction, SimulationTransaction
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def get_simulation_transaction(id: ObjectId, db: Database, cache: Redis):
    simulation_transaction_collection = db.simulation_transactions
    transaction = await lazyload(cache, f'simulation_transaction:{id}', loader=simulation_transaction_collection.find_one, params={'_id': id})

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Simulation Transaction not found: {str(id)}')
    
    features = await hound_transaction(SimulationTransaction(**transaction), db)
    transaction['features'] = {k: v for k, v in features.items() if k not in transaction}
    return DataResponse[AnalyzedSimulationTransaction](data=transaction)