from typing import List

from pymongo.database import Database
from src.models.simulation_devices import ListSimulationDevices, SimulationDevice
from src.lib.utils.pagination import sort_mapping
from src.lib.utils.response import DataResponse


async def list_simulation_devices(payload: ListSimulationDevices, db: Database):
    simulation_device_collection = db.simulation_devices
    query = payload.model_dump(exclude=['limit', 'skip', 'sort', 'query'], exclude_none=True)
    if payload.query is not None:
        query = {
            **query,
            **{
                '$or': [
                    {'name': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'device_id': {'$regex': f'^{payload.query}', "$options": "i"}},
                ]
            }
        }

    data = (await simulation_device_collection.find(query)
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit)
        .skip(payload.skip)
        .to_list())
    
    return DataResponse[List[SimulationDevice]](data=data)
