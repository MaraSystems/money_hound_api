from typing import List

from pymongo.database import Database
from src.domains.simulation_accounts.model import ListSimulationAccounts, SimulationAccount
from src.lib.utils.pagination import sort_mapping
from src.lib.utils.response import DataResponse


async def list_simulation_accounts(payload: ListSimulationAccounts, db: Database):
    simulation_account_collection = db.simulation_accounts
    query = payload.model_dump(exclude=['limit', 'skip', 'sort', 'query'], exclude_none=True)
    if payload.query is not None:
        query = {
            **query,
            **{
                '$or': [
                    {'account_no': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'account_name': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'bank_name': {'$regex': f'^{payload.query}', "$options": "i"}}
                ]
            }
        }

    data = (await simulation_account_collection.find(query)
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit)
        .skip(payload.skip)
        .to_list())
    
    return DataResponse[List[SimulationAccount]](data=data)
