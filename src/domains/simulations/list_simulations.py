from typing import List


from pymongo.database import Database
from src.domains.simulations.model import ListSimulations, Simulation
from src.lib.utils.pagination import sort_mapping
from src.lib.utils.response import DataResponse


async def list_simulations(payload: ListSimulations, db: Database):
    simulation_collection = db.simulations
    query = {'hidden': False}
    if payload.author_id is not None:
        query = {
            **query,
            **{'author_id': payload.author_id}
        }

    data = (await simulation_collection.find(query)
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit)
        .skip(payload.skip)
        .to_list())
    
    return DataResponse[List[Simulation]](data=data)
