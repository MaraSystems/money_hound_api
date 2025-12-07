from src.lib.analytics import tracker
from src.lib.store.load_data import load_data
from config.config import BANK_DEVICES_CSV, ACCOUNTS_CSV, ANALYZED_TRANSACTIONS_CSV, ENGINEERED_TRANSACTIONS_CSV, LOCATION_CSV


def list_accounts(exclude=''):
    analyzed_transactions_df = load_data(ANALYZED_TRANSACTIONS_CSV, parse_dates=['time'])
    accounts = [item for item in analyzed_transactions_df['holder'].unique() if item not in exclude]
    return accounts


def get_account(account_no):
    accounts_df = load_data(ACCOUNTS_CSV)
    accounts_df['devices'] = accounts_df['devices'].apply(lambda x: x.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(','))
    return accounts_df[accounts_df['account_no'] == account_no].to_dict(orient='records')[0]


def list_states():
    location_df = load_data(LOCATION_CSV)
    return location_df['state'].unique()


def select_location(state):
    location_df = load_data(LOCATION_CSV)
    return location_df[location_df['state'] == state].sample(1).to_dict(orient='records')[0]


def list_devices():
    accounts_df = load_data(ACCOUNTS_CSV)
    accounts_df['devices'] = accounts_df['devices'].apply(lambda x: x.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(','))
    return accounts_df.sample(n=1).iloc[0]['devices']


def get_transactions(target, value):
    engineered_transactions_df = load_data(ENGINEERED_TRANSACTIONS_CSV, parse_dates=['time'])
    return engineered_transactions_df[engineered_transactions_df[target] == value]


def get_merchants(lat, lon):
    accounts_df = load_data(ACCOUNTS_CSV)
    accounts_df['devices'] = accounts_df['devices'].apply(lambda x: x.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(','))
    merchant_list = accounts_df[accounts_df['merchant']].copy()
    merchant_list['distance'] = merchant_list.apply(
        lambda merchant: 
        tracker.distance(
            latA=lat,
            lonA=lon,
            latB=merchant['latitude'],
            lonB=merchant['longitude']
        ),
        axis=1
    )
    merchant_list.sort_values(by='distance', inplace=True)
    merchant_list.index = merchant_list['account_no'] + ' ' + merchant_list['state'] + ' ('+ merchant_list['distance'].astype(str).str.slice(stop=4) + 'KM)'
    return merchant_list


def get_atms(lat, lon):
    bank_devices_df = load_data(BANK_DEVICES_CSV)
    atm_list = bank_devices_df.copy()
    atm_list['distance'] = atm_list.apply(
        lambda merchant: 
        tracker.distance(
            latA=lat,
            lonA=lon,
            latB=merchant['latitude'],
            lonB=merchant['longitude']
        ),
        axis=1
    )
    atm_list.sort_values(by='distance', inplace=True)
    atm_list.index = atm_list['device_id'] + ' ' + atm_list['state'] + ' ('+ atm_list['distance'].astype(str).str.slice(stop=4) + 'KM)'
    return atm_list