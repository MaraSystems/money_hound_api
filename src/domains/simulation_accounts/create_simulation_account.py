from pymongo.database import Database
from redis.asyncio import Redis
from fastapi import status, HTTPException

from src.domains.simulation_accounts.model import SimulationAccount, CreateSimulationAccount
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def create_simulation_account(payload: CreateSimulationAccount, db: Database, cache: Redis) -> DataResponse[SimulationAccount]:
    simulation_account_collection = db.simulation_accounts
    simulation_profile_collection = db.simulation_profiles

    profile = await lazyload(cache, f'simulation_profile:{payload.bvn}', loader=simulation_profile_collection.find_one, params={'filter': {'user_id': payload.bvn, 'simulation_id': payload.simulation_id}})

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Simulation Profile not found: {str(payload.bvn)}')

    if profile['name'] != payload.account_name:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Account name does not match BVN name: {str(profile['name'])}")

    accounts = (await simulation_account_collection.find({'simulation_id': payload.simulation_id, 'bank_name': payload.bank_name})
        .to_list()    
    )

    payload.account_no = f"ACC_{(len(accounts) + 1):010}"
    insert = await simulation_account_collection.insert_one(payload.model_dump())
    account = await simulation_account_collection.find_one({'_id': insert.inserted_id})

    return DataResponse(data=SimulationAccount(**account), message='Simulation Account created successfully')
