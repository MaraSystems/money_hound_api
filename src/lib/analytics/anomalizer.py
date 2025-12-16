import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import IsolationForest

from src.lib.analytics import engineer, extractor


def anomalize(df: pd.DataFrame, name, columns=[]):
    """
        Flag and score anomalies

        @param df: The dataframe to use
        @param name: The name of the anomaly
        @param columns: The columns to check for anomalies

        returns pd.DataFrame
    """

    # Copy the data
    df = df.copy()
    columns = df.columns if len(columns) == 0 else columns

    # Extract the required columns
    data = df[columns]

    # Initialize IsolationForest and fit the data
    model_IF = IsolationForest(random_state=42)
    model_IF.fit(data)

    # Flag and Score anamalies
    scores = model_IF.decision_function(data)
    flags = model_IF.predict(data)
    
    # Normalize the flag and score
    anomaly = [True if x == -1 else False for x in flags]
    anomaly_scores = (scores.max() - scores) / (scores.max() - scores.min())

    # Save the flag and score
    df[f'{name}_score'] = anomaly_scores
    df[name] = anomaly
    return df


def unsual_amount(df):
    # detect unsual amounts
    columns = [
        'large_amount', 'large_amount_drain', 'large_amount_pump', 
        'holder_amount_bound_frequency', 
        'holder_large_amount_drain_True_occurance', 'holder_large_amount_pump_True_occurance', 
        'holder_amount_avg_30D'
    ]
    return anomalize(df, 'unsual_amount', columns)


def unsual_balance(df):
    # detect unsual balances
    columns = [
        'balance_jump_rate', 'balance_jump_rate_absolute', 'drained_balance', 'pumped_balance', 
        'holder_balance_jump_bound_frequency', 'holder_balance_jump_rate_bound_frequency', 
        'holder_drained_balance_True_occurance', 'holder_pumped_balance_True_occurance', 
        'holder_balance_avg_30D'
    ]
    return anomalize(df, 'unsual_balance', columns)


def unsual_location(df):
    # detect unsual locations
    columns = [
        'distance_from_home (km)', 
        'far_distance',
        'holder_far_distance_True_occurance',
        'holder_distance_from_home (km)_avg_30D'
    ]
    return anomalize(df, 'unsual_location', columns)


def unsual_device(df):
    # detect unsual devices
    columns = ['holder_device_count_frequency', 'holder_device_has_history', 'is_opening_device', 'holder_holder_device_count_frequency_avg_30D']
    return anomalize(df, 'unsual_device', columns)


def unsual_time(df):
    # detect unsual time
    columns = [
        'holder_hour_bound_frequency', 'holder_holder_hour_bound_frequency_avg_30D'
    ]
    return anomalize(df, 'unsual_time', columns)


def check_unusual(df: pd.DataFrame):
    df['time'] = str(df['time'])
    discrete_features = df.select_dtypes(exclude=['number']).columns.tolist()
    encoded = engineer.encoder(df, discrete_features)
    df[discrete_features] = encoded

    scaler = RobustScaler()
    scaled_data = scaler.fit_transform(df)
    df = pd.DataFrame(scaled_data, columns=df.columns)

    df_unsual = df.copy()
    df_unsual = unsual_amount(df_unsual)
    df_unsual = unsual_balance(df_unsual)
    df_unsual = unsual_location(df_unsual)
    df_unsual = unsual_time(df_unsual)
    df_unsual = unsual_device(df_unsual)

    return anomalize(df_unsual, 'fraud')


def detect_fraud(df: pd.DataFrame, accounts_df: pd.DataFrame):
    """
        Analyze the dataframe and plot the results

        @param df: The transaction dataframe to analyze
        @param accounts_df: The accounts dataframe to analyze

        returns pd.DataFrame
    """
    df = df.apply(lambda row: extractor.extract_account_features(row, accounts_df), axis=1)
    df = df.apply(extractor.extract_time_features, axis=1)
    df = df.apply(extractor.extract_money_features, axis=1)
    df = df.apply(lambda row: extractor.extract_location_features(df, row), axis=1)
    df = df.apply(lambda row: extractor.extract_frequency_features(df, row), axis=1)
    df = extractor.extract_bounds(df, 'holder')
    df = extractor.extract_holder_occurance(df)
    df = extractor.extract_holder_bvn_occurance(df)
    df = extractor.extract_related_occurance(df)
    df = extractor.extract_related_bvn_occurance(df)
    df = extractor.extract_rolling_averages(df)

    fraud_df = check_unusual(df.copy())
    columns = [c for c in fraud_df.columns if c not in df.columns]
    df[columns] = fraud_df[columns]

    return df

