
from pymongo.database import Database
from pandas import DataFrame
from pymongo import DESCENDING

from src.domains.simulation_transactions.model import InitiateSimulationTransaction, SimulationTransaction
from src.lib.analytics.extractor import extract_account_features, extract_frequency_features, extract_money_features, extract_time_features, extract_location_features, extract_bounds, extract_holder_bvn_occurance, extract_holder_occurance, extract_related_bvn_occurance, extract_related_occurance, extract_rolling_averages
from src.lib.analytics.anomalizer import check_unusual, detect_fraud


async def hound_transaction(transaction: SimulationTransaction, db: Database):
    simulation_transaction_collection = db.simulation_transactions
    simulation_account_collection = db.simulation_accounts

    accounts = await simulation_account_collection.find({'simulation_id': transaction.simulation_id}).to_list()

    base_query = {'simulation_id': transaction.simulation_id, 'time': {'$lte': transaction.time}}

    holder_history = await simulation_transaction_collection.find({
        **base_query, 'holder': transaction.holder, 'holder_bank': transaction.holder_bank
    }).sort({'time': DESCENDING}).to_list(length=1000)

    related_history = await simulation_transaction_collection.find({
        **base_query, 'related': transaction.related, 'related_bank': transaction.related_bank
    }).sort({'time': DESCENDING}).to_list(length=1000)

    public_history = await simulation_transaction_collection.find({
        **base_query, 
        '$nor': [
            {'holder': transaction.holder, 'holder_bank': transaction.holder_bank},
            {'related': transaction.related, 'related_bank': transaction.related_bank},
        ]
    }).sort({'time': DESCENDING}).to_list(length=1000)

    history = holder_history + related_history + public_history + [transaction.model_dump()]

    df = DataFrame(history).sort_values(by='time', ascending=False)
    accounts_df = DataFrame(accounts)
    fraud_df = detect_fraud(df, accounts_df)
    return fraud_df.to_dict(orient='records')[0]

