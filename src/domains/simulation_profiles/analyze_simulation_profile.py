from typing import Any


from pandas import DataFrame
from pymongo import DESCENDING
from pymongo.database import Database
from bson import ObjectId
from redis.asyncio import Redis

from src.domains.simulation_profiles.get_simulation_profile import get_simulation_profile
from src.domains.simulation_transactions.analyze_transaction_history import analyze_transaction_history
from src.domains.simulation_transactions.model import TransactionsAnalysis
from src.lib.utils.response import DataResponse


async def analyze_simulation_profile(id: ObjectId, db: Database, cache: Redis):
    profile_response = await get_simulation_profile(id, db, cache)
    profile_data = profile_response.data
    simulation_transaction_collection = db.simulation_transactions
    simulation_account_collection = db.simulation_accounts

    transactions = await simulation_transaction_collection.find({'simulation_id': profile_data.simulation_id}).sort({'time': DESCENDING}).to_list()
    accounts = await simulation_account_collection.find({'simulation_id': profile_data.simulation_id}).to_list()

    transaction_analysis = await analyze_transaction_history(
        DataFrame(transactions), 
        DataFrame(accounts),
        extract=['holder_bvn', 'related_bvn'],
        filter_transactions=lambda df: df[
            (df['holder_bvn'] == profile_data.user_id) | (df['related_bvn'] == profile_data.user_id)
        ]
    )    
    return DataResponse[TransactionsAnalysis](data=transaction_analysis)