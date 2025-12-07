import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import RobustScaler, MinMaxScaler, LabelEncoder

from src.lib.analytics import detector, engineer


from ..store.load_data import load_data
from config.config import ENGINEERED_TRANSACTIONS_CSV
from src.lib.analytics import tracker

def unusual(data):
    data['date'] = str(data['date'])

    engineered_transactions_df = load_data(ENGINEERED_TRANSACTIONS_CSV, parse_dates=['time'])
    old_df = engineered_transactions_df
    df = pd.concat([old_df, data]).set_index('time')

    discrete_features = df.select_dtypes(include=['object']).columns.tolist()
    encoded = engineer.encoder(df, discrete_features)
    df[discrete_features] = encoded

    scaler = RobustScaler()
    scaled_data = scaler.fit_transform(df)
    df = pd.DataFrame(scaled_data, columns=df.columns)

    df_unsual = df.copy()
    df_unsual = detector.unsual_amount(df_unsual)
    df_unsual = detector.unsual_balance(df_unsual)
    df_unsual = detector.unsual_location(df_unsual)
    df_unsual = detector.unsual_time(df_unsual)
    df_unsual = detector.unsual_device(df_unsual)

    df_fruad = engineer.anomalize(df_unsual, 'fraud')
    return df_fruad.tail(1)
