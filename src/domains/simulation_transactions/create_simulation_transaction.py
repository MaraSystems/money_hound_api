from uuid import uuid4
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.simulation_accounts.model import SimulationAccount
from src.domains.simulation_transactions.analyze_transaction import analyze_transaction
from src.domains.simulation_transactions.get_simulation_transaction import get_simulation_transaction
from src.domains.simulation_transactions.model import CreateSimulationTransaction, InitiateSimulationTransaction, SimulationTransaction
from src.domains.simulation_transactions.transact import credit_account, debit_account
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def create_simulation_transaction(payload: InitiateSimulationTransaction, db: Database, cache: Redis) -> DataResponse[SimulationTransaction]:
    simulation_account_collection = db.simulation_accounts

    holder_account: SimulationAccount = await lazyload(
        cache, f'simulation_account:{payload.holder}:{payload.holder_bank}', 
        loader=simulation_account_collection.find_one, 
        params={'account_no': payload.holder, 'bank_name': payload.holder_bank}
    )

    related_account: SimulationAccount = await lazyload(
        cache, f'simulation_account:{payload.related}:{payload.related_bank}', 
        loader=simulation_account_collection.find_one, 
        params={'account_no': payload.related, 'bank_name': payload.related_bank}
    )

    reference = str(uuid4())
    transaction = None

    if payload.type == 'CREDIT':
        await debit_account(related_account, holder_account, payload, reference, db, cache)
        transaction = await credit_account(holder_account, related_account, payload, reference, db, cache)
    else:
        transaction = await debit_account(holder_account, related_account, payload, reference, db, cache)
        await credit_account(related_account, holder_account, payload, reference, db, cache)

    return DataResponse(data=transaction, message=f'Transaction created successfully: {payload.amount}')



