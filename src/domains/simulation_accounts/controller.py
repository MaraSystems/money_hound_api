from bson import ObjectId
import os
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from pymongo.database import Database

from src.domains.auth.model import CurrentUser
from src.domains.simulation_accounts.get_simulation_account import get_simulation_account
from src.domains.simulation_accounts.list_simulation_accounts import list_simulation_accounts
from src.domains.simulation_accounts.model import ListSimulationAccounts, SimulationAccount
from src.config.cache import get_cache
from src.config.database import get_db
from src.lib.utils.response import DataResponse
from src.middlewares.auth_guard import get_current_user


simulation_accounts_router = APIRouter(prefix='/simulation_accounts')

# @simulation_accounts_router.post(
#     '', 
#     response_model=DataResponse[SimulationAccount],
#     status_code=201,
#     name="Create Simulation accounts")
# async def create(
#     payload: CreateSimulation,
#     user=Depends(get_current_user), 
#     db: Database = Depends(get_db)
# ):
#     return await create_simulation(payload, str(user.id), db)


@simulation_accounts_router.get(
    '/{id}', 
    response_model=DataResponse[SimulationAccount], 
    name="Get Simulation accounts"
)
async def get(
    id: str,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[SimulationAccount]:
    return await get_simulation_account(ObjectId(id), db, cache)


@simulation_accounts_router.get(
    '',
    response_model=DataResponse[List[SimulationAccount]],
    name="List Simulation accounts"
)
async def fetch_list(
    payload: Annotated[Query, Depends(ListSimulationAccounts)],
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db)
) -> DataResponse[List[SimulationAccount]]:
    return await list_simulation_accounts(payload, db)