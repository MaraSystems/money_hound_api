from typing import List

from pymongo.database import Database
from src.models.simulation_profile import ListSimulationProfiles, SimulationProfile
from src.models.pagination import sort_mapping
from src.models.response import DataResponse, PageResponse


async def list_simulation_profiles(payload: ListSimulationProfiles, db: Database) -> PageResponse[SimulationProfile]:
    simulation_profile_collection = db.simulation_profiles
    query = payload.model_dump(exclude=['limit', 'skip', 'sort', 'query'], exclude_none=True)
    if payload.query is not None:
        query = {
            **query,
            **{
                '$or': [
                    {'user_name': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'name': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'email': {'$regex': f'^{payload.query}', "$options": "i"}}
                ]
            }
        }

    data = (await simulation_profile_collection.find(query)
        .limit(payload.limit+1)
        .skip(payload.skip * payload.limit)
        .to_list())
    
    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)

