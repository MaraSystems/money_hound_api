import pandas as pd
import numpy as np

def trail(before_df: pd.DataFrame, transaction_row, run):
    """Run function only on prior rows for a single transaction."""
    return run(before_df, transaction_row)


def hound(df: pd.DataFrame, run=lambda d, t: (d, t)):
    """
    For each row in df, apply run() to all rows before it in time.
    Returns a list of results.
    """
    df_sorted = df.sort_values('time')  # Ensure transactions are time-ordered
    results = []

    # Keep a running 'history' slice without filtering entire df each time
    history = pd.DataFrame(columns=df.columns)

    for row in df_sorted.itertuples(index=False):
        # Call run on history
        results.append(run(history, row._asdict()))
        # Append current row to history
        new_row = pd.DataFrame([row._asdict()])
        if not new_row.dropna(how='all').empty:
            history = pd.concat([history, new_row], ignore_index=True)

    return results


def distance(latA, lonA, latB, lonB):
    # Get the distance between 2 locations

    # Radius of the earth
    R = 6371

    # Convert degrees to radians
    latA, lonA, latB, lonB = map(np.radians, [latA, lonA, latB, lonB])

    # Difference
    lat_diff = latB - latA
    lon_diff = lonB - lonA

    # Haversine formular
    a = np.sin(lat_diff / 2.0)**2 + np.cos(latA) * np.cos(latB) * np.sin(lon_diff / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


def rolling_averages(df, group, features, window):
    """
        Add rolling averages grouped by `group` back to original DataFrame.

        @params df: The dataframe to use.
        @params group: How the dataframe should be grouped.
        @params features: The features to roll.
        @params window: Number of days to roll.

        @returns df: A dataframe containing the original dataframe and the rolled values.
    """

    # Copy the dataframe
    df = df.sort_values([group, "date"]).copy()
    data = df[[group, *features]]

    columns = []
    for feature in features:
        # Name the average feature
        rolled_col = f"{group}_{feature}_avg_{window}D"
        columns.append(rolled_col)

        # Group and get the average of the feature within the window
        df[rolled_col] = (
            data.groupby(group)[feature]
              .transform(lambda x: x.rolling(window, min_periods=1).mean())
        )
    
    return df[columns]



