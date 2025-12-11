import pandas as pd

from src.lib.analytics import engineer, tracker

def extract_account_features(data, accounts: pd.DataFrame):
    holder_account = accounts[(accounts['account_no'] == data['holder']) & (accounts['bank_name'] == data['holder_bank'])].iloc[0]

    related_accounts = accounts[(accounts['account_no'] == data['related']) & (accounts['bank_name'] == data['related_bank'])]

    data['holder_bvn'] = holder_account['bvn']
    data['kyc'] = holder_account['kyc']
    data['merchant'] = holder_account['merchant']
    data['holder_bvn'] = holder_account['bvn']
    data['related_bvn'] = related_accounts.iloc[0]['bvn'] if not related_accounts.empty else data['related_bank']
    data['sub_account'] = data['holder_bvn'] == data['related_bvn']
    data['is_opening_device'] = data['device'] == holder_account['opening_device']

    return data


def extract_money_features(data):
    transaction_limits = {1: 50_000, 2: 100_000, 3: 500_000, 4: 1_000_000}

    data['large_amount'] = transaction_limits[data['kyc']] < data['amount']
    data['balance_jump'] = -data['amount'] if data['type'] == 'DEBIT' else data['amount']
    data['previous_balance'] = data['balance'] - data['balance_jump']
    data['balance_jump_rate'] = data['balance_jump'] / max(data['previous_balance'], 1)
    data['balance_jump_rate_absolute'] = abs(data['balance_jump_rate'])
    data['drained_balance'] = data['balance_jump_rate'] < -.9
    data['pumped_balance'] = data['balance_jump_rate'] > .9
    data['large_amount_drain'] = data['large_amount'] & data['drained_balance']
    data['large_amount_pump'] = data['large_amount'] & data['pumped_balance']
    return data


def extract_time_features(data):
    dt = pd.to_datetime(data['time'])
    data['hour'] = dt.hour

    # Extracting the day
    data['week_day'] = dt.day_name()

    # Extracting the month
    data['month'] = dt.month_name()

    # Extracting the date
    data['date'] = dt.date()

    # Extracting the month day
    data['month_day'] = int(dt.day)

    return data


def extract_location_features(df: pd.DataFrame, data):
    data['central_latitude'], data['central_longitude'] = engineer.central_location(df, data, 'holder')
    data['distance_from_home (km)'] = engineer.distance_from_home(data, data, 'holder')
    data['far_distance'] = data['distance_from_home (km)'] >= 100
    return data


def extract_frequency_features(df: pd.DataFrame, data):
    holder_df = df[(df['holder'] == data['holder']) & (df['holder_bank'] == data['holder_bank'])]
    holder_bvn_df = df[(df['holder_bvn'] == data['holder_bvn'])]

    # related_df = df.get_transactions('related', data['related'])
    # related_bvn_df = df.get_transactions('related_bvn', data['related_bvn'])

    holder_count_frequency = {f'holder_{feature}_count_frequency': engineer.count_related(holder_df, data, target='holder', feature=feature) for feature in ['related', 'device', 'channel']}

    holder_bvn_count_frequency = {f'holder_bvn_{feature}_count_frequency': engineer.count_related(holder_bvn_df, data, target='holder_bvn', feature=feature) for feature in ['related_bvn', 'device', 'channel']}

    for key, value in { **holder_count_frequency, **holder_bvn_count_frequency }.items():
        data[key] = value

    data['holder_device_has_history'] = data['holder_device_count_frequency'] > 0

    return data


def extract_bounds(df: pd.DataFrame, key):
    bounds = [
        # Has user ever transacted around this hour
        { 'name': 'hour', 'bound': lambda x: (x-1, x+1) }, 

        # Has user ever had balance around this balance
        { 'name': 'balance', 'bound': lambda x: (x*.5, x*1.5) }, 

        # Has user ever made a transaction around this amount
        { 'name': 'amount', 'bound': lambda x: (x*.5, x*1.5) },
        
        # Has user balance ever jumped like this before
        { 'name': 'balance_jump', 'bound': lambda x: (x * 0.5, x * 1.5) },

        # Relative balance jump rate (percentage-like scaling)
        { 'name': 'balance_jump_rate', 'bound': lambda x: (x - 0.2, x + 0.2) },
        { 'name': 'balance_jump_rate_absolute', 'bound': lambda x: (x - 0.2, x + 0.2) }
    ]

    return engineer.get_bound_relations_frequency(df, key, bounds)


def extract_holder_occurance(df: pd.DataFrame):
    # Get the occurance of the following features with the account holder
    occurances = [
        { 'name': 'reported', 'value': True },
        { 'name': 'category', 'value': 'REVERSAL' },
        { 'name': 'drained_balance', 'value': True },
        { 'name': 'pumped_balance', 'value': True },
        { 'name': 'large_amount_drain', 'value': True },
        { 'name': 'large_amount_pump', 'value': True },
        { 'name': 'far_distance', 'value': True }
    ]

    return engineer.get_occurrence_count(df, 'holder', occurances)


def extract_holder_bvn_occurance(df: pd.DataFrame):
    # Get the occurance of the following features with the account holder_bvn
    occurances = [
        { 'name': 'reported', 'value': True },
        { 'name': 'category', 'value': 'REVERSAL' },
        { 'name': 'far_distance', 'value': True }
    ]

    return engineer.get_occurrence_count(df, 'holder_bvn', occurances)


def extract_related_occurance(df: pd.DataFrame):
    # Get the occurance of the following features with the account related
    occurances = [
        { 'name': 'reported', 'value': True },
        { 'name': 'category', 'value': 'REVERSAL' }
    ]

    return engineer.get_occurrence_count(df, 'related', occurances)


def extract_related_bvn_occurance(df: pd.DataFrame):
    # Get the occurance of the following features with the account related_bvn
    occurances = [
        { 'name': 'reported', 'value': True },
        { 'name': 'category', 'value': 'REVERSAL' }
    ]

    return engineer.get_occurrence_count(df, 'related_bvn', occurances)


def extract_rolling_averages(df):
    # Get the rolling average of these features

    rolling_features = [
        # Transaction dynamics
        'amount', 'balance', 'balance_jump', 'balance_jump_rate',

        # Distance
        'distance_from_home (km)',  
        
        # Device usage
        'holder_device_count_frequency', 

        # Time
        'holder_hour_bound_frequency',

        # Holder - Related relationship
        'holder_related_count_frequency',
        
        # Reversal Tracking
        'holder_category_REVERSAL_occurance',

        # Reported Tracking
        'holder_reported_True_occurance'
    ]

    # Get for the specified windows
    window_1 = tracker.rolling_averages(df, 'holder', rolling_features, 1)
    window_7 = tracker.rolling_averages(df, 'holder', rolling_features, 7)
    window_30 = tracker.rolling_averages(df, 'holder', rolling_features, 30)
    window_120 = tracker.rolling_averages(df, 'holder', rolling_features, 120)

    data = pd.concat([df, window_1, window_7, window_30, window_120], axis=1)
    return data
    