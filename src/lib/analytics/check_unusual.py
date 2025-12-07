import pandas as pd
from sklearn.preprocessing import RobustScaler

from src.lib.analytics import detector, engineer

def check_unusual(df: pd.DataFrame):
    df['time'] = str(df['time'])
    discrete_features = df.select_dtypes(exclude=['number']).columns.tolist()
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

    return engineer.anomalize(df_unsual, 'fraud')
