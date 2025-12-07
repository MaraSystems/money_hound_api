from typing import List

from pymongo.database import Database
from src.domains.simulation_transactions.model import ListSimulationTransactions, SimulationTransaction
from src.lib.utils.pagination import sort_mapping
from src.lib.utils.response import DataResponse


async def list_simulation_transactions(payload: ListSimulationTransactions, db: Database):
    simulation_transaction_collection = db.simulation_transactions
    query = payload.model_dump(exclude=['limit', 'skip', 'sort', 'query'], exclude_none=True)
    if payload.query is not None:
        query = {
            **query,
            **{
                '$or': [
                    {'holder': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'holder_bank': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'reference': {'$regex': f'^{payload.query}', "$options": "i"}}
                ]
            }
        }

    data = (await simulation_transaction_collection.find(query)
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit)
        .skip(payload.skip)
        .to_list())
    
    return DataResponse[List[SimulationTransaction]](data=data)
