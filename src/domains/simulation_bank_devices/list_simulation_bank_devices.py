from typing import List

from pymongo.database import Database
from src.domains.simulation_bank_devices.model import ListSimulationBankDevices, SimulationBankDevice
from src.lib.utils.pagination import sort_mapping
from src.lib.utils.response import DataResponse


async def list_simulation_bank_devices(payload: ListSimulationBankDevices, db: Database):
    simulation_bank_device_collection = db.simulation_bank_devices
    query = payload.model_dump(exclude=['limit', 'skip', 'sort', 'query'], exclude_none=True)
    if payload.query is not None:
        query = {
            **query,
            **{
                '$or': [
                    {'bank_name': {'$regex': f'^{payload.query}', "$options": "i"}},
                    {'device_id': {'$regex': f'^{payload.query}', "$options": "i"}},
                ]
            }
        }

    data = (await simulation_bank_device_collection.find(query)
        .sort('created_at', sort_mapping[payload.sort])
        .limit(payload.limit)
        .skip(payload.skip)
        .to_list())
    
    return DataResponse[List[SimulationBankDevice]](data=data)
