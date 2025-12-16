from typing import Any


from pandas import DataFrame
from pymongo import DESCENDING
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulation_transactions.analyze_transaction_history import analyze_transaction_history
from src.domains.simulation_transactions.model import TransactionsAnalysis
from src.domains.simulations.get_simulation import get_simulation
from src.lib.utils.response import DataResponse


async def analyze_simulation(id: ObjectId, db: Database, cache: Redis):
    await get_simulation(id, db, cache)
    simulation_transaction_collection = db.simulation_transactions
    simulation_account_collection = db.simulation_accounts

    transactions = await simulation_transaction_collection.find({'simulation_id': str(id)}).sort({'time': DESCENDING}).to_list()
    accounts = await simulation_account_collection.find({'simulation_id': str(id)}).to_list()

    transaction_analysis = await analyze_transaction_history(DataFrame(transactions), DataFrame(accounts))
    return DataResponse[TransactionsAnalysis](data=transaction_analysis)