from typing import List

from pymongo.database import Database
from src.models.simulation_account import ListSimulationAccounts, SimulationAccount
from src.models.pagination import sort_mapping
from src.models.response import DataResponse, PageResponse


async def list_simulation_accounts(payload: ListSimulationAccounts, db: Database) -> PageResponse[SimulationAccount]:
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
        .limit(payload.limit+1)
        .skip(payload.skip * payload.limit)
        .to_list())
    
    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)
