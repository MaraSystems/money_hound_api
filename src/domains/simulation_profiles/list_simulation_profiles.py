from typing import List

from pymongo.database import Database
from src.domains.simulation_profiles.model import ListSimulationProfiles, SimulationProfile
from src.lib.utils.pagination import sort_mapping
from src.lib.utils.response import DataResponse


async def list_simulation_profiles(payload: ListSimulationProfiles, db: Database):
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
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit)
        .skip(payload.skip)
        .to_list())
    
    return DataResponse[List[SimulationProfile]](data=data)
