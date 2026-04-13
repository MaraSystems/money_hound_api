from pymongo.database import Database
from src.models.simulation_devices import ListSimulationDevices, SimulationDevice
from src.models.pagination import sort_mapping
from src.models.response import  PageResponse


async def list_simulation_devices(payload: ListSimulationDevices, db: Database) -> PageResponse[SimulationDevice]:
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
        .limit(payload.limit+1)
        .skip(payload.skip * payload.limit)
        .to_list())
    
    has_more = len(data) > payload.limit
    return PageResponse(skip=payload.skip, limit=payload.limit, data=data[0:payload.limit], has_more=has_more)
