from bson import ObjectId
import os
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from pymongo.database import Database

from src.domains.auth.model import CurrentUser
from src.domains.simulation_bank_devices.get_simulation_bank_device import get_simulation_bank_device
from src.domains.simulation_bank_devices.list_simulation_bank_devices import list_simulation_bank_devices
from src.domains.simulation_bank_devices.model import ListSimulationBankDevices, SimulationBankDevice
from src.config.cache import get_cache
from src.config.database import get_db
from src.lib.utils.response import DataResponse
from src.middlewares.auth_guard import get_current_user


simulation_bank_devices_router = APIRouter(prefix='/simulation_bank_devices')

# @simulation_bank_devices_router.post(
#     '', 
#     response_model=DataResponse[SimulationBankDevice],
#     status_code=201,
#     name="Create Simulation bank_devices")
# async def create(
#     payload: CreateSimulation,
#     user=Depends(get_current_user), 
#     db: Database = Depends(get_db)
# ):
#     return await create_simulation(payload, str(user.id), db)


@simulation_bank_devices_router.get(
    '/{id}', 
    response_model=DataResponse[SimulationBankDevice], 
    name="Get Simulation Bank Device"
)
async def get(
    id: str,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[SimulationBankDevice]:
    return await get_simulation_bank_device(ObjectId(id), db, cache)


@simulation_bank_devices_router.get(
    '',
    response_model=DataResponse[List[SimulationBankDevice]],
    name="List Simulation Bank Devices"
)
async def fetch_list(
    payload: Annotated[Query, Depends(ListSimulationBankDevices)],
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db)
) -> DataResponse[List[SimulationBankDevice]]:
    return await list_simulation_bank_devices(payload, db)