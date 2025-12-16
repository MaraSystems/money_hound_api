import pandas as pd
from sklearn.preprocessing import LabelEncoder

from .tracker import distance


def encoder(df, features):
    """
    Encode categorical features using Label Encoding.

    @param: df (pd.DataFrame): The DataFrame to process.
    @param: features (list): The list of features to encode.
    """
    
    feature_df = pd.DataFrame(index=df.index)
    for col in features:
        feature_df[col] = LabelEncoder().fit_transform(df[col])

    return feature_df


def count_related(df: pd.DataFrame, transaction, target, feature):
    # Count the frequency of relations between target and feature
    return len(df[(df[target] == transaction[target]) & (df[feature] == transaction[feature])])


def get_cashflow(df: pd.DataFrame, group):
    """
        Get the cashflow with respect to the provided group

        @params group: the feature to group 
    """
    
    # Find groups with the highest volumn of transacionts
    cash_flow = df.groupby([group, 'type'])['amount'].sum().sort_values(ascending=False).to_frame().reset_index()

    # Get the netflow for each group
    cash_flow_pivot = cash_flow.pivot_table(index=group, columns='type', values='amount', aggfunc='sum').reset_index()

    cash_flow_pivot['DEBIT'] = 0 if 'DEBIT' not in cash_flow_pivot.columns else cash_flow_pivot['DEBIT']
    cash_flow_pivot['CREDIT'] = 0 if 'CREDIT' not in cash_flow_pivot.columns else cash_flow_pivot['CREDIT']
    
    cash_flow_pivot['NETFLOW'] = cash_flow_pivot['CREDIT'] - cash_flow_pivot['DEBIT']

    # Add the netflow for each group
    for netflow in cash_flow_pivot[[group, 'NETFLOW']].itertuples(index=False):
        cash_flow = pd.concat([cash_flow, pd.DataFrame({group: [netflow[0]], 'type': 'NETFLOW', 'amount': [netflow.NETFLOW]})], ignore_index=True)

    return cash_flow


def bound_relation(df: pd.DataFrame, transaction, target, feature):
    # Check if the feature is within the bounds for the specified target
    name = feature['name']
    value = df[name]

    # Check if in bound
    (low, high) = feature['bound'](value)
    tx_value = transaction[name]

    # Return the number of times this feature was in bound
    return len(df[(df[target] == transaction[target]) & (low <= tx_value) & (tx_value <= high)])


def count_occurrence(df: pd.DataFrame, transaction, target, feature, value):
    # Get the number of times this feature has occured with this value
    return len(df[(df[target] == transaction[target]) & (df[feature] == value)])


def get_occurrence_count(df: pd.DataFrame, target, features):
    """
        Get the occurance count for a feature with a specified value

        @param df: The dataframe
        @param target: The column to match
        @params features: The name and value of the features to get the occurance count
    """

    # Copy the dataframe
    df = df.sort_values(by='time').copy()

    # Extract the required columns
    data = df[[target, *[x['name'] for x in features]]]
    
    # Initialize the counter and store
    counts_dict = {feat['name']: {} for feat in features}
    results = {f"{target}_{feat['name']}_{feat['value']}_occurance": [] for feat in features}
    
    for idx, row in data.iterrows(): # For each row in dataframe
        for feat in features: 
            feat_name = feat['name']
            feat_value = feat['value']
            row_value = row[feat_name]
            key = (row[target], row[feat_name]) # Set the store key

            # Check if in bound
            if row_value == feat_value:
                # Get current count
                count = counts_dict[feat_name].get(key, 0)
                results[f"{target}_{feat_name}_{feat_value}_occurance"].append(count)
                # Update count
                counts_dict[feat_name][key] = count + 1
            else:
                # Out of bounds → count 0
                results[f"{target}_{feat_name}_{feat_value}_occurance"].append(0)

    # Add the counts to the dataframe
    for col, vals in results.items():
        df[col] = vals

    return df


def duration_from_last(df: pd.DataFrame, transaction, target):
    transaction_list = df[df[target] == transaction[target]]
    if transaction_list.empty:
        return 0
    
    last_transaction = transaction_list.tail(1).iloc[0]
    duration = (transaction['time'] - last_transaction['time']).total_seconds() / 3600
    return duration


def distance_from_last(df: pd.DataFrame, transaction, target):
    transaction_list = df[df[target] == transaction[target]]
    if transaction_list.empty:
        return 0
    
    last_transaction = transaction_list.iloc[-1]
    last_geo = (last_transaction['latitude'], last_transaction['longitude'])
    current_geo = (transaction['latitude'], transaction['longitude'])

    return distance(*last_geo, *current_geo)


def distance_from_home(df: pd.DataFrame, transaction, target):
    # Get the distance from home of user
    home_geo = (transaction['central_latitude'], transaction['central_longitude'])
    current_geo = (transaction['latitude'], transaction['longitude'])

    return distance(*home_geo, *current_geo)


def central_location(df: pd.DataFrame, transaction, target):
    # Get the mean location of the target
    transaction_list = df[df[target] == transaction[target]]
    if transaction_list.empty:
        return (transaction['latitude'], transaction['longitude'])
    
    mean_lat = transaction_list['latitude'].mean()
    mean_lon = transaction_list['longitude'].mean()

    return (mean_lat, mean_lon)


def get_bound_relations_frequency(df: pd.DataFrame, target, features):
    """
        Get the number of times with feature is within bounds

        @param df: The dataframe
        @param target: The column to match
        @params features: The name and value of the features to get the occurance count
    """
    # Copy the dataframe
    df = df.sort_values(by='time').copy()
    data = df[[target, *[x['name'] for x in features]]]
    
    # Prepare dictionaries
    counts_dict = {feat['name']: {} for feat in features}
    results = {f"{target}_{feat['name']}_bound_frequency": [] for feat in features}

    # Precompute bounds per feature
    bounds = {feat['name']: feat['bound'](data[feat['name']]) for feat in features}
    # Iterate over rows
    for idx, row in data.iterrows():
        for feat in features:
            feat_name = feat['name']
            key = (row[target], row[feat_name])
            row_value = row[feat_name]
            low, high = bounds[feat_name]
            
            # Check if in bound
            if low.iloc[idx] <= row_value <= high.iloc[idx]:
                # Get current count
                count = counts_dict[feat_name].get(key, 0)
                results[f"{target}_{feat_name}_bound_frequency"].append(count)
                # Update count
                counts_dict[feat_name][key] = count + 1
            else:
                # Out of bounds → count 0
                results[f"{target}_{feat_name}_bound_frequency"].append(0)

    # Add results as columns
    for col, vals in results.items():
        df[col] = vals

    return df


def get_count_relations_frequency(df: pd.DataFrame, target, features):
    """
        Get the number of times this target has related to the specified feature 

        @param df: The dataframe
        @param target: The column to match
        @params features: The name and value of the features to get the occurance count
    """
    df = df.sort_values(by='time').copy()
    data = df[[target, *features]]
    
    counts_dict = {feat: {} for feat in features}
    frequencies = {f"{target}_{feat}_count_frequency": [] for feat in features}
    has_history = {f"{target}_{feat}_has_history": [] for feat in features}

    for idx, row in data.iterrows():
        for feat in features:
            key = (row[target], row[feat])
            count = counts_dict[feat].get(key, 0)
            frequencies[f"{target}_{feat}_count_frequency"].append(count)
            has_history[f"{target}_{feat}_has_history"].append(count > 0)
            counts_dict[feat][key] = count + 1

    for col, vals in frequencies.items():
        df[col] = vals
        history_col = col.replace('count_frequency', 'has_history')
        df[history_col] = has_history[history_col]

    return df
    