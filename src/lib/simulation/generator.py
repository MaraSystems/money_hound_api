from faker import Faker
from faker.providers import profile, bank
import numpy as np
import pandas as pd
import random
import math

from src.lib.analytics import tracker

fake = Faker()
Faker.seed(42)
fake.add_provider(profile)
fake.add_provider(bank)


def generate_amount(level=1, limit=0):
    """
        Generate a random amount.

        @param level: The level of the account.
        @param limit: The maximum amount to generate.

        @return: A random amount.
    """

    # Set the bounds for amount
    max_amount = limit if limit else  (10 ** level) * 10000

    # Generate a random amount and round it 2 decimal places to mimic money.
    return round(np.random.uniform(100, max_amount), 2) 


async def random_location(location_df: pd.DataFrame, lat=None, lon=None):
    """
        Select a random location from location_df (vectorized & fast).

        @params lat: The latitude
        @params lon: The longitude

        @returns a random location(lon, lat)
    """


    limits = [1, 10, 100, 1000, 10000]
    radius = random.uniform(0, random.choices(limits, [1, .5, .1, .05, .001], k=1)[0])
    locations = location_df.copy()

    if lat is not None and lon is not None:
        distances = locations.apply(
            lambda location: 
            tracker.distance(
                latA=lat,
                lonA=lon,
                latB=location['latitude'],
                lonB=location['longitude']
            ),
            axis=1
        )

        # Filter within radius
        nearby = locations.loc[distances <= radius]
        if not nearby.empty:
            locations = nearby

    # fallback: pick any location
    return locations.sample(n=1).squeeze()


async def random_account(accounts: pd.DataFrame, exclude):
    """
        Select a random account number from the accounts.

        @param accounts: The dataframe contianing the accounts

        @return: An account
    """
    level = random.choices([1, 2, 3, 4], [1, 2, 3, 4], k=1)[0]
    
    # Select a random account
    selected = accounts[accounts['account_no'] != exclude]
    filtered = selected.loc[selected['kyc'] >= level]

    if filtered.empty:
        filtered = selected

    return filtered.sample(n=1).squeeze()


async def random_merchant(profiles: pd.DataFrame, accounts: pd.DataFrame, lat, lon):
    """
        Select a random merchant from the merchants DataFrame

        @param profiles: The dataframe contianing the profiles
        @param accounts: The dataframe contianing the accounts
        @params lat: The latitude
        @params lon: The longitude

        @returns: a random account that is a merchant within the set location(lon, lat)
    """

    # Get the list of merchants
    merchants_list = accounts[accounts['merchant']]
    if merchants_list.empty:
        return

    # Get the users who are merchants
    merchant_users_list = profiles[profiles['user_id'].isin(merchants_list['bvn'])].copy()

    # Pick radius
    limits = [1, 10, 100, 1000, 10000]
    radius = random.uniform(0, random.choices(limits, [1, .5, .1, .05, .001], k=1)[0])

    # Calculate the distance of merchants
    merchant_users_list['distance'] = merchant_users_list.apply(
        lambda merchant: 
        tracker.distance(
            latA=lat,
            lonA=lon,
            latB=merchant['latitude'],
            lonB=merchant['longitude']
        ),
        axis=1
    )

    # Filter by radius
    nearby = merchant_users_list.loc[merchant_users_list['distance'] <= radius]

    # Select a merchant
    if not nearby.empty:
        merchant_id = nearby.sample(n=1).squeeze()['user_id']
        merchants_list = merchants_list[merchants_list['bvn'] == merchant_id]

    # Final merchant details
    merchant = merchants_list.sample(n=1).squeeze()    
    user_id = merchant['bvn']
    device_id = f'POS_{user_id.split("_")[-1]}'
    user = profiles[profiles['user_id'] == user_id].squeeze()

    return {
        'latitude': user['latitude'],
        'longitude': user['longitude'],
        'device_id': device_id,
        'account_no': merchant['account_no'],
        'bvn': user_id,
        'bank_name': merchant['bank_name'],
        'balance': merchant['balance']
    }


async def random_atm(bank_devices: pd.DataFrame, lat, lon):
    """
        Select a random bank device from bank_devices

        @param bank_devices: The dataframe contianing the bank_devices
        @params lat: The latitude
        @params lon: The longitude

        @returns: a random account that is a merchant within the set location(lon, lat)
    """

    # Pick radius
    limits = [1, 10, 100, 1000, 10000]
    radius = random.uniform(0, random.choices(limits, [1, .5, .1, .05, .001], k=1)[0])

    # Calculate the distance of merchants
    distances = bank_devices.apply(
        lambda bank_device: 
        tracker.distance(
            latA=lat,
            lonA=lon,
            latB=bank_device['latitude'],
            lonB=bank_device['longitude']
        ),
        axis=1
    )

    # Filter by radius
    candidates = bank_devices.loc[distances <= radius]

    # Select a bank device
    if candidates.empty:
        candidates = bank_devices
    
    bank_device = candidates.sample(n=1).squeeze()

    return {
        'latitude': bank_device['latitude'],
        'longitude': bank_device['longitude'],
        'device_id': bank_device['device_id'],
        'account_no': bank_device['device_id'],
        'bvn': bank_device['device_id'],
        'bank_name': bank_device['bank_name'],
    }


async def random_user_device(individuals: dict):
    profiles = pd.DataFrame([individual.profile for individual in individuals.values()])
    return random.choice(profiles.sample(n=1).squeeze()['devices'])