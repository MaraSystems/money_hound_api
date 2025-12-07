import pandas as pd
from sklearn.preprocessing import RobustScaler, MinMaxScaler, LabelEncoder

from src.lib.analytics import engineer

from ..store import dataframe
from ..store.load_data import load_data
from config.config import ENGINEERED_TRANSACTIONS_CSV
from src.lib.analytics import tracker

def extract(data):
    transaction_limits = {1: 50_000, 2: 100_000, 3: 500_000, 4: 1_000_000}

    data['sub_account'] = data['holder_bvn'] == data['related_bvn']
    data['large_amount'] = transaction_limits[data['kyc']] < data['amount']
    data['balance_jump'] = -data['amount'] if data['type'] == 'DEBIT' else data['amount']
    data['previous_balance'] = data['balance'] - data['balance_jump']
    data['balance_jump_rate'] = data['balance_jump'] / max(data['previous_balance'], 1)
    data['balance_jump_rate_absolute'] = abs(data['balance_jump_rate'])
    data['drained_balance'] = data['balance_jump_rate'] < -.9
    data['pumped_balance'] = data['balance_jump_rate'] > .9
    data['large_amount_drain'] = data['large_amount'] & data['drained_balance']
    data['large_amount_pump'] = data['large_amount'] & data['pumped_balance']

    df = pd.DataFrame([data])
    df['hour'] = df['time'].dt.hour

    # Extracting the day
    df['week_day'] = df['time'].dt.day_name()

    # Extracting the month
    df['month'] = df['time'].dt.month_name()

    # Extracting the date
    df['date'] = df['time'].dt.date

    # Extracting the month day
    df['month_day'] = df['time'].dt.day.astype('object')
    
    time = df[['hour', 'week_day', 'month', 'date', 'month_day']].to_dict(orient='records')[0]
    data = { **data, **time }

    account = dataframe.get_account(data['holder'])
    holder_df = dataframe.get_transactions('holder', data['holder'])
    holder_bvn_df = dataframe.get_transactions('holder_bvn', data['holder_bvn'])
    related_df = dataframe.get_transactions('related', data['related'])
    related_bvn_df = dataframe.get_transactions('related_bvn', data['related_bvn'])

    data['distance_from_home (km)'] = engineer.distance_from_home(holder_df, data, 'holder')
    data['far_distance'] = data['distance_from_home (km)'] >= 100

    holder_count_frequency = {f'holder_{feature}_count_frequency': engineer.count_related(holder_df, data, target='holder', feature=feature) for feature in ['related', 'device', 'channel', 'state']}

    holder_bvn_count_frequency = {f'holder_bvn_{feature}_count_frequency': engineer.count_related(holder_bvn_df, data, target='holder_bvn', feature=feature) for feature in ['related_bvn', 'device', 'channel', 'state']}

    data = { **data, **holder_count_frequency, **holder_bvn_count_frequency }
    data['holder_device_has_history'] = data['holder_device_count_frequency'] > 0
    data['is_opening_device'] = data['device'] == account['opening_device']

    data_df = pd.DataFrame([data])
    columns = data_df.columns

    engineered_transactions_df = load_data(ENGINEERED_TRANSACTIONS_CSV, parse_dates=['time'])
    new_df = pd.concat([engineered_transactions_df[columns].sample(5000), data_df], axis=0, ignore_index=True)

    new_df = engineer.get_bounds(new_df)
    new_df = engineer.get_holder_occurance(new_df)
    new_df = engineer.get_holder_bvn_occurance(new_df)
    new_df = engineer.get_related_occurance(new_df)
    new_df = engineer.get_related_bvn_occurance(new_df)
    
    new_df = tracker.get_rolling(new_df)
    return new_df.tail(1)
