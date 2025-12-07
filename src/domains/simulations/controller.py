from bson import ObjectId
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from pymongo.database import Database

from src.domains.auth.model import CurrentUser
from src.domains.simulations.delete_simulation import delete_simulation
from src.domains.simulations.get_simulation import get_simulation
from src.domains.simulations.list_simulations import list_simulations
from src.domains.simulations.model import CreateSimulation, Simulation, ListSimulations, UpdateSimulation
from src.domains.simulations.create_simulation import create_simulation
from src.config.cache import get_cache
from src.config.database import get_db
from src.domains.simulations.update_simulation import update_simulation
from src.lib.utils.response import DataResponse
from src.middlewares.auth_guard import get_current_user


simulations_router = APIRouter(prefix='/simulations')

@simulations_router.post(
    '', 
    response_model=DataResponse[Simulation],
    status_code=201,
    name="Initiate Simulation")
async def create(
    payload: CreateSimulation,
    user=Depends(get_current_user), 
    db: Database = Depends(get_db)
):
    return await create_simulation(payload, str(user.id), db)


@simulations_router.get(
    '/{id}', 
    response_model=DataResponse[Simulation], 
    name="Get Simulation"
)
async def get(
    id: str, 
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[Simulation]:
    return await get_simulation(ObjectId(id), db, cache)


@simulations_router.get(
    '',
    response_model=DataResponse[List[Simulation]],
    name="List Simulations"
)
async def fetch_list(
    payload: Annotated[Query, Depends(ListSimulations)],
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db)
) -> DataResponse[List[Simulation]]:
    return await list_simulations(payload, db)


@simulations_router.patch(
    '/{id}', 
    response_model=DataResponse[Simulation], 
    name="Update Simulation"
)
async def update(
    id: str, 
    payload: UpdateSimulation,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[Simulation]:
    return await update_simulation(ObjectId(id), payload, str(user.id), db, cache)


@simulations_router.delete(
    '/{id}',
    response_model=DataResponse[None],
    name="Delete Simulation"
)
async def delete(
    id: str,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[None]:
    return await delete_simulation(ObjectId(id), str(user.id), db, cache)
