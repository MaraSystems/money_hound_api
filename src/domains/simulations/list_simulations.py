from typing import List


from pymongo.database import Database
from src.models.simulation import ListSimulations, Simulation
from src.models.pagination import sort_mapping
from src.models.response import DataResponse, PageResponse


async def list_simulations(payload: ListSimulations, db: Database) -> PageResponse[Simulation]:
    simulation_collection = db.simulations
    query = {'hidden': False}
    if payload.author_id is not None:
        query = {
            **query,
            **{'author_id': payload.author_id}
        }

    data = (await simulation_collection.find(query)
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit+1)
        .skip(payload.skip * payload.limit)
        .to_list())
    
    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)

