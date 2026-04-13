import asyncio
from pandas import DataFrame
from redis.asyncio import Redis
from pymongo.database import Database
from bson import ObjectId

from src.db.cache import get_cache
from src.lib.utils.config import UPLOAD_PATH
from src.db.database import get_db
from src.tasks.queue import celery_app
from src.models.simulation_account import CreateSimulationAccount
from src.models.simulation_devices import CreateSimulationDevice
from src.models.simulation_profile import CreateSimulationProfile
from src.models.simulation import Simulation
from src.models.simulation_transaction import CreateSimulationTransaction
from src.models.user import User
from src.lib.simulation.simulator import Simulator
from src.lib.utils.lazycache import lazyload
from src.lib.utils.logger import get_logger
from src.tasks.send_mail import send_mail_task
from src.lib.utils.config import ENV, ENVIRONMENTS
from src.tasks.send_mail import send_mail_task
from src.lib.task.run_task import run_task


async def run_simulation(payload: Simulation, user_id: str, db: Database, cache: Redis):
    period = 60 * 60 * 24
    sim = Simulator(
        num_users=payload.get('min_num_user', 5),
        num_banks=payload.get('num_banks', 5),
        min_amount=payload.get('min_amount', None),
        max_amount=payload.get('max_amount', None),
        geo=(payload.get('latitude', 9), payload.get('longitude', 3)),
        radius=payload.get('radius', None),
        fraudulence=payload.get('fraudulence', None)
    )

    await sim.setup_reality()
    await sim.simulate(period, payload['days'])
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
    user_details: User = await lazyload(cache, f'user:{user_id}', loader=user_collection.find_one, params={'_id': ObjectId(user_id), 'hidden': False})

    transactions = prepare_data(sim.generated_data, payload, 'transactions')
    transactions = [CreateSimulationTransaction(**item).model_dump() for item in transactions]
    simulation_transaction_collection = db.simulation_transactions  
    await simulation_transaction_collection.insert_many(transactions)

    bank_devices = prepare_data(sim.generated_data, payload, 'bank_devices')
    bank_devices = [CreateSimulationDevice(**item).model_dump() for item in bank_devices]
    simulation_devices_collection = db.simulation_devices 
    await simulation_devices_collection.insert_many(bank_devices)

    profiles = prepare_data(sim.generated_data, payload, 'profiles')
    profiles = [CreateSimulationProfile(**item).model_dump() for item in profiles]
    simulation_profiles_collection = db.simulation_profiles 
    await simulation_profiles_collection.insert_many(profiles)

    accounts = prepare_data(sim.generated_data, payload, 'accounts')
    accounts = [CreateSimulationAccount(**item).model_dump() for item in accounts]
    simulation_accounts_collection = db.simulation_accounts
    await simulation_accounts_collection.insert_many(accounts)

    run_task(
        send_mail_task,
        kwargs={
            'subject': 'Simulation Complete',
            'email': user_details['email'],
            'data': {
                'user_name': user_details['firstname'],
                'num_banks': payload['num_banks'],
                'timestamp': payload['created_at']
            },
            'template_file': 'simulation_complete.html',
            'attatchments': sim.datasets
        }
    )

    logger.info(f"Simulation Saved")


@celery_app.task(name='run_simulation_task')
def run_simulation_task(payload: Simulation, user_id: str):
    if ENV == ENVIRONMENTS.TESTING:
        return

    async def run():
        db: Database = await get_db()
        cache: Redis = get_cache()
        await run_simulation(payload, user_id, db, cache)

    asyncio.run(run())
