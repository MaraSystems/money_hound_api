from typing import Any


from pandas import DataFrame
from pymongo import DESCENDING
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulation_accounts.get_simulation_account import get_simulation_account
from src.domains.simulation_transactions.analyze_transaction_history import analyze_transaction_history
from src.domains.simulation_transactions.model import TransactionsAnalysis
from src.lib.utils.response import DataResponse


async def analyze_simulation_account(id: ObjectId, db: Database, cache: Redis):
    account_response = await get_simulation_account(id, db, cache)
    account_data = account_response.data
    simulation_transaction_collection = db.simulation_transactions
    simulation_account_collection = db.simulation_accounts

    transactions = await simulation_transaction_collection.find({'simulation_id': account_data.simulation_id}).sort({'time': DESCENDING}).to_list()
    accounts = await simulation_account_collection.find({'simulation_id': account_data.simulation_id}).to_list()

    transaction_analysis = await analyze_transaction_history(
        DataFrame(transactions), 
        DataFrame(accounts),
        filter_transactions=lambda df: df[
            ((df['holder'] == account_data.account_no) & (df['holder_bank'] == account_data.bank_name))
            | 
            ((df['related'] == account_data.account_no) & (df['related_bank'] == account_data.bank_name))
        ]
    )
    return DataResponse[TransactionsAnalysis](data=transaction_analysis)