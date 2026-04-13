from bson import ObjectId
import os
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from pymongo.database import Database

from src.models.auth import CurrentUser
from src.domains.simulation_transactions.create_simulation_transaction import create_simulation_transaction
from src.domains.simulation_transactions.get_simulation_transaction import get_simulation_transaction
from src.domains.simulation_transactions.list_simulation_transactions import list_simulation_transactions
from src.models.simulation_transaction import AnalyzedSimulationTransaction, ListSimulationTransactions, SimulationTransaction, InitiateSimulationTransaction
from src.db.cache import get_cache
from src.db.database import get_db
from src.models.response import DataResponse, PageResponse
from src.middlewares.auth_guard import get_current_user


simulation_transactions_router = APIRouter(prefix='/simulation_transactions')

@simulation_transactions_router.post(
    '', 
    response_model=DataResponse[AnalyzedSimulationTransaction],
    status_code=201,
    name="Create Simulation Transaction")
async def create(
    payload: InitiateSimulationTransaction,
    user=Depends(get_current_user), 
    db: Database = Depends(get_db),
    cache=Depends(get_cache)
):
    return await create_simulation_transaction(payload, db, cache)


@simulation_transactions_router.get(
    '/{id}', 
    response_model=DataResponse[AnalyzedSimulationTransaction], 
    name="Get Simulation Transactions"
)
async def get(
    id: str,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[AnalyzedSimulationTransaction]:
    return await get_simulation_transaction(ObjectId(id), db, cache)


@simulation_transactions_router.get(
    '',
    response_model=PageResponse[SimulationTransaction],
    name="List Simulation Transactions"
)
async def fetch_list(
    payload: Annotated[Query, Depends(ListSimulationTransactions)],
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db)
) -> PageResponse[SimulationTransaction]:
    return await list_simulation_transactions(payload, db)
