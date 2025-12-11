from bson import ObjectId
import os
from typing import Annotated, List
from fastapi import Depends, Query
from fastapi.routing import APIRouter
from pymongo.database import Database

from src.domains.auth.model import CurrentUser
from src.domains.simulation_profiles.create_simulation_profile import create_simulation_profile
from src.domains.simulation_profiles.get_simulation_profile import get_simulation_profile
from src.domains.simulation_profiles.list_simulation_profiles import list_simulation_profiles
from src.domains.simulation_profiles.model import CreateSimulationProfile, ListSimulationProfiles, SimulationProfile
from src.config.cache import get_cache
from src.config.database import get_db
from src.lib.utils.response import DataResponse
from src.middlewares.auth_guard import get_current_user


simulation_profiles_router = APIRouter(prefix='/simulation_profiles')

@simulation_profiles_router.post(
    '', 
    response_model=DataResponse[SimulationProfile],
    status_code=201,
    name="Create Simulation Profiles")
async def create(
    payload: CreateSimulationProfile,
    user=Depends(get_current_user), 
    db: Database = Depends(get_db),
    cache=Depends(get_cache)
):
    return await create_simulation_profile(payload, db, cache)


@simulation_profiles_router.get(
    '/{id}', 
    response_model=DataResponse[SimulationProfile], 
    name="Get Simulation Profiles"
)
async def get(
    id: str,
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache),
) -> DataResponse[SimulationProfile]:
    return await get_simulation_profile(ObjectId(id), db, cache)


@simulation_profiles_router.get(
    '',
    response_model=DataResponse[List[SimulationProfile]],
    name="List Simulation Profiles"
)
async def fetch_list(
    payload: Annotated[Query, Depends(ListSimulationProfiles)],
    user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db)
) -> DataResponse[List[SimulationProfile]]:
    return await list_simulation_profiles(payload, db)