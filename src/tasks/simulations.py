import asyncio
from pandas import DataFrame
from redis.asyncio import Redis
from pymongo.database import Database
from bson import ObjectId

from src.config.cache import get_cache
from src.config.config import UPLOAD_PATH
from src.config.database import get_db
from src.config.queue import celery_app
from src.domains.simulation_accounts.model import CreateSimulationAccount
from src.domains.simulation_bank_devices.model import CreateSimulationBankDevice
from src.domains.simulation_profiles.model import CreateSimulationProfile
from src.domains.simulations.model import Simulation
from src.domains.simulation_transactions.model import CreateSimulationTransaction
from src.domains.users.model import User
from src.lib.simulation.simulator import Simulator
from src.lib.utils.lazycache import lazyload
from src.lib.utils.logger import get_logger
from src.tasks.mailer import send_mail
from src.config.config import ENV, ENVIRONMENTS


async def run_simulation(payload: Simulation, user_id: str, db: Database, cache: Redis):
    period = 60 * 60 * 24
    sim = Simulator()

    await sim.setup_reality(
        num_users=payload.get('min_num_user', 5),
        num_banks=payload.get('num_banks', 5),
        min_amount=payload.get('min_amount', None),
        max_amount=payload.get('max_amount', None),
        geo=(payload.get('latitude', 9), payload.get('longitude', 3)),
        radius=payload.get('radius', None),
        fraudulence=payload.get('fraudulence', None)
    )

    await sim.simulate(
        period,
        payload['days']
    )
    
    await save_simulation(payload, user_id, sim, db, cache)


def prepare_data(generated_data, payload, key):
    data = generated_data[key]
    data['simulation_id'] = payload['_id']
    data = data.to_dict(orient='records')
    return data


async def save_simulation(payload: Simulation, user_id: str, sim: Simulator, db: Database, cache: Redis):
    logger = get_logger('Simulation Logger')

    path = f"{UPLOAD_PATH}/simulations/{payload['_id']}"
    await sim.save_data(path)

    logger.info(f"Simulation Completed")
    
    simulation_collection = db.simulations
    await simulation_collection.update_one({'_id': ObjectId(payload['_id'])}, {'$set': {'status': 'COMPLETE'}})

    user_collection = db.users
    user_details: User = await lazyload(cache, f'user:{user_id}', loader=user_collection.find_one, params={'filter': {'_id': ObjectId(user_id), 'hidden': False}})

    transactions = prepare_data(sim.generated_data, payload, 'transactions')
    transactions = [CreateSimulationTransaction(**item).model_dump() for item in transactions]
    simulation_transaction_collection = db.simulation_transactions  
    await simulation_transaction_collection.insert_many(transactions)

    bank_devices = prepare_data(sim.generated_data, payload, 'bank_devices')
    bank_devices = [CreateSimulationBankDevice(**item).model_dump() for item in bank_devices]
    simulation_bank_devices_collection = db.simulation_bank_devices 
    await simulation_bank_devices_collection.insert_many(bank_devices)

    profiles = prepare_data(sim.generated_data, payload, 'profiles')
    profiles = [CreateSimulationProfile(**item).model_dump() for item in profiles]
    simulation_profiles_collection = db.simulation_profiles 
    await simulation_profiles_collection.insert_many(profiles)

    accounts = prepare_data(sim.generated_data, payload, 'accounts')
    accounts = [CreateSimulationAccount(**item).model_dump() for item in accounts]
    simulation_accounts_collection = db.simulation_accounts
    await simulation_accounts_collection.insert_many(accounts)

    send_mail.delay(
        'Simulation Complete',
        user_details['email'], 
        {
            'user_name': user_details['firstname'],
            'num_banks': payload['num_banks'],
            'timestamp': payload['created_at']
        }, 
        'simulation_complete.html', 
        sim.datasets
    )

    logger.info(f"Simulation Saved")


@celery_app.task
def simulator(payload: Simulation, user_id: str):
    if ENV == ENVIRONMENTS.TESTING:
        return

    async def run():
        db: Database = await get_db()
        cache: Redis = get_cache()
        await run_simulation(payload, user_id, db, cache)

    asyncio.run(run())
