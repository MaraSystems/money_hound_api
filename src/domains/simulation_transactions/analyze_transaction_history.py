import pandas as pd

from src.domains.simulation_transactions.hound_transaction import hound_transaction
from src.domains.simulation_transactions.model import AnalyzedSimulationTransaction, SimulationTransaction, TransactionsAnalysis
from src.lib.analytics.anomalizer import detect_fraud
from src.lib.analytics.engineer import get_cashflow
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def analyze_transaction_history(df: pd.DataFrame, accounts_df: pd.DataFrame, extract = [], filter_transactions = lambda df: df):
    fraud_df = detect_fraud(df, accounts_df)
    df[['fraud_score', 'fraud', 'week_day']] = fraud_df[['fraud_score', 'fraud', 'week_day']]
    df['hour'] = fraud_df['hour'].astype('str')
    df[extract] = fraud_df[extract]

    df = filter_transactions(df)
    numerical_columns = ['amount', 'balance', 'time', 'latitude', 'longitude', 'fraud_score']
    numerical = df[numerical_columns].describe().drop(index=['count']).to_dict(orient='index')
    
    categorical_columns = ['channel', 'category', 'type', 'fraud', 'hour']
    categorical = df[categorical_columns].describe().drop(index=['count']).to_dict(orient='index')

    columns = ['channel', 'category', 'week_day', 'fraud', 'hour']
    volumns = {c: get_cashflow(df, c).to_dict(orient='records') for c in columns}

    proportions = {c: df[c].value_counts(normalize=True).to_frame().to_dict(orient='index') for c in columns}
    return TransactionsAnalysis(numerical=numerical, categorical=categorical, volumns=volumns, proportions=proportions)
