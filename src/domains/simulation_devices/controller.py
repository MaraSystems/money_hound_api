from bson import ObjectId
import os
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from pymongo.database import Database

from src.domains.auth.model import CurrentUser
from src.domains.simulation_devices.get_simulation_device import get_simulation_device
from src.domains.simulation_devices.list_simulation_devices import list_simulation_devices
from src.models.simulation_devices import ListSimulationDevices, SimulationDevice
from src.db.cache import get_cache
from src.db.database import get_db
from src.lib.utils.response import DataResponse
from src.middlewares.auth_guard import get_current_user


simulation_devices_router = APIRouter(prefix='/simulation_devices')

# @simulation_devices_router.post(
#     '', 
#     response_model=DataResponse[SimulationDevice],
#     status_code=201,
#     name="Create Simulation devices")
# async def create(
#     payload: CreateSimulation,
#     user=Depends(get_current_user), 
#     db: Database = Depends(get_db)
# ):
#     return await create_simulation(payload, str(user.id), db)


@simulation_devices_router.get(
    '/{id}', 
    response_model=DataResponse[SimulationDevice], 
    name="Get Simulation  Device"
)
async def get(
    id: str,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[SimulationDevice]:
    return await get_simulation_device(ObjectId(id), db, cache)


@simulation_devices_router.get(
    '',
    response_model=DataResponse[List[SimulationDevice]],
    name="List Simulation Devices"
)
async def fetch_list(
    payload: Annotated[Query, Depends(ListSimulationDevices)],
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db)
) -> DataResponse[List[SimulationDevice]]:
    return await list_simulation_devices(payload, db)