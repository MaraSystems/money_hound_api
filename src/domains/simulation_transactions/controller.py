from bson import ObjectId
import os
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from pymongo.database import Database

from src.domains.auth.model import CurrentUser
from src.domains.simulation_transactions.get_simulation_transaction import get_simulation_transaction
from src.domains.simulation_transactions.list_simulation_transactions import list_simulation_transactions
from src.domains.simulation_transactions.model import ListSimulationTransactions, SimulationTransaction
from src.config.cache import get_cache
from src.config.database import get_db
from src.lib.utils.response import DataResponse
from src.middlewares.auth_guard import get_current_user


simulation_transactions_router = APIRouter(prefix='/simulation_transactions')

# @simulation_transactions_router.post(
#     '', 
#     response_model=DataResponse[SimulationTransaction],
#     status_code=201,
#     name="Create Simulation Transaction")
# async def create(
#     payload: CreateSimulation,
#     user=Depends(get_current_user), 
#     db: Database = Depends(get_db)
# ):
#     return await create_simulation(payload, str(user.id), db)


@simulation_transactions_router.get(
    '/{id}', 
    response_model=DataResponse[SimulationTransaction], 
    name="Get Simulation Transactions"
)
async def get(
    id: str,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[SimulationTransaction]:
    return await get_simulation_transaction(ObjectId(id), db, cache)


@simulation_transactions_router.get(
    '',
    response_model=DataResponse[List[SimulationTransaction]],
    name="List Simulation Transactions"
)
async def fetch_list(
    payload: Annotated[Query, Depends(ListSimulationTransactions)],
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db)
) -> DataResponse[List[SimulationTransaction]]:
    return await list_simulation_transactions(payload, db)