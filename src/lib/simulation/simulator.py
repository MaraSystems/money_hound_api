from time import sleep
import math
from pathlib import Path
import random
import pandas as pd
import asyncio
import stat
import os
from uuid import uuid4

from src.lib.analytics import extractor
from src.lib.analytics.anomalizer import check_unusual
from src.lib.simulation import banking, clock
from src.lib.simulation.individual import Individual
from src.lib.simulation.events import Events
from src.lib.simulation.generator import generate_amount
from src.lib.simulation.generator import fake


class Simulator:
    """
        Simulate the banking system.
    """

    def __init__(self):
        """
            Initialize a banking system

            @param min_amount: The minimum amount to transact
        """


    async def generate_locations(self, count=1000):
        degrees = self.radius / 111_320
        locations = []

        for _ in range(count):
            radius = degrees * math.sqrt(random.random())
            theta = random.random() * 2 * math.pi
            
            lat, lon = self.geo
            new_lat = lat + radius * math.cos(theta)
            new_lon = lon + (radius * math.sin(theta)) / math.cos(math.radians(lat))

            locations.append({'latitude': new_lat, 'longitude': new_lon})

        self.locations = pd.DataFrame(locations)


    async def setup_individuals(self, num_users: int):
        """
            Sets up individuals for the simulation

            @param num_users: The number of users
        """
        # Generate all the individuals
        self.individuals = {}
        for _ in range(num_users):
            # Initialize the bank
            individual = Individual(locations=self.locations)

            await individual.setup()
            self.individuals[individual.profile['user_id']] = individual


    async def setup_banks(self, num_banks: int):
        """
            Sets up banks for the simulation

            @param bank_names: The names of banks
        """
        # Reset the banks in the simulation
        self.banks = {}
        profiles = [individual.profile for individual in self.individuals.values()]
        min_accounts = int(len(profiles) * .3)


        # Generate a bank for each bank name
        for _ in range(num_banks):
            # Initialize the bank
            name = f'{fake.name()} Bank'
            bank = banking.Bank(name, locations=self.locations, fraudulence=self.fraudulence)

            await bank.setup(num_devices=random.randint(3, 5), users=random.sample(profiles, random.randint(min_accounts, min_accounts * 2)))
            self.banks[name] = bank


    async def setup_reality(self, num_users: int, num_banks: int, min_amount = 100, max_amount = 5_000_000, geo=(9.3, 3.9), radius=50_000, fraudulence = .05):
        """
            Sets the reality for the simulation
            
            @param num_users: The number of users
            @param bank_names: The names of banks
        """

        self.geo = geo
        self.radius = radius
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.fraudulence = fraudulence

        await self.generate_locations()
        await self.setup_individuals(num_users)
        await self.setup_banks(num_banks)
        self.events = Events(banks=self.banks, individuals=self.individuals, locations=self.locations)
        

    async def run_event(self):
        """
            Run an events that can take place in the banking process
        """

        # Selects a random account to initiate event
        accounts = pd.concat([bank.accounts for bank in self.banks.values()])
        account = accounts[accounts['balance'] >= self.min_amount].sample(n=1).squeeze()
        balance = account['balance']

        # Decide on amount for transaction
        spend_limit = random.choices([.1, .4, .7, 1], [.7, .19, .109, self.fraudulence], k=1)[0] * balance

        limit = spend_limit if spend_limit > self.min_amount else balance 
        limit = spend_limit if spend_limit < self.max_amount else self.max_amount
        
        amount = generate_amount(level=account['kyc'], limit=limit)

        # Generate transaction reference
        reference = str(uuid4())

        individual: Individual = self.individuals[account['bvn']]

        # Set the account holders details
        holder = {
            'account_no': account['account_no'],
            'bvn': account['bvn'],
            'bank_name': account['bank_name'],
            'balance': account['balance'],
            'latitude': individual.profile['latitude'],
            'longitude': individual.profile['longitude']
        }


        # Will transaction be reversed?
        reverse = random.random() < self.fraudulence

        # Play event
        event = await self.events.spin(individual)
        await event(holder, amount, reference, {'reverse': reverse})

        # A new user comes in
        if random.random() > .995:
            if random.random() > .5:
                new_individual = Individual(self.locations)
                await new_individual.setup()
                self.individuals[new_individual.profile['user_id']] = new_individual
                self.events.individuals = self.individuals
            else:
                await self.banks[account['bank_name']].open_account(individual.profile)


    async def run_batches(self):
        """
            Run events in batches
        """

        # setup a batch
        async with self.semaphore:
            await self.run_event()


    async def simulate(self, period, iterations, batch_size=20, seed=42, wait_time=0):
        """
            Simulate banking processes

            @param period: The period of the simulation
            @param iteration: The iteration of periods
            @param batch_size: The number of events to run at once
            @param seed: The seed for the random number generator
            @param fraudulence: The percentage of fraudulence
            @param wait_time: The time to wait between batches
        """

        self.semaphore = asyncio.Semaphore(batch_size)
        
        # Set a seed for familiar generation
        random.seed(seed)

        # Reset the clock
        clock.global_clock.reset()

        # Calculation the duration of the simulation
        duration = period * iterations

        # Initialize the milestone
        milestone = 0

        # Run for each scene
        while (duration > clock.global_clock.ticker):

            # Factoring time for sleep and low transaction volumn
            batch_events = lambda: asyncio.gather(*[self.run_batches() for _ in range(batch_size)])
            if clock.global_clock.now().hour <= 6:
                await batch_events() if random.random() > .7 else clock.global_clock.advance(10)
            else:
                await batch_events()

            progress = clock.global_clock.ticker // period
            if milestone < progress:
                milestone = progress
                print(f'Season: {milestone}')

            # Advance the clock
            clock.global_clock.advance(wait_time)
            sleep(wait_time)


        print('Simulation complete.')

    
    async def extract_data(self):
        transactions = pd.concat([bank.transactions for bank in self.banks.values()])
        bank_devices = pd.concat([bank.devices for bank in self.banks.values()])
        profiles = pd.DataFrame([individual.profile for individual in self.individuals.values()])
        accounts = pd.concat([bank.accounts for bank in self.banks.values()])
        accounts = accounts.reset_index().merge(
            profiles.reset_index()[['latitude', 'longitude', 'devices', 'user_id', 'name', 'gender', 'email', 'birthdate']], 
            how='left', 
            left_on='bvn', 
            right_on='user_id'
        ).drop(columns=['user_id', 'index'])

        self.generated_data = {'transactions': transactions, 'bank_devices': bank_devices, 'profiles': profiles, 'accounts': accounts}
        return self.generated_data


    async def save_data(self, path='../datasets'):
        data = await self.extract_data()
        self.datasets = []

        target_dir = Path(path)
        target_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(target_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        for name, dataframe in data.items():
            file_path = target_dir / f'{name}.csv'
            self.datasets.append(str(file_path))
            dataframe.to_csv(file_path, index=False)


    async def engineer_features(self):
        df = self.generated_data['transactions'].reset_index(drop=True)
        accounts_df = self.generated_data['accounts']

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

        return check_unusual(df)


def get_simulator():
    simulator = Simulator()
    return simulator