import random
import pandas as pd
from uuid import uuid4
from collections import defaultdict
import asyncio

from src.lib.simulation.generator import random_location
from src.lib.simulation.generator import generate_amount
from src.lib.simulation.clock import global_clock


class Bank:
    """
        Simulate the operation of a bank
    """

    def __init__(self, name: str, locations: pd.DataFrame, transactions: pd.DataFrame = pd.DataFrame(), accounts: pd.DataFrame = pd.DataFrame(), devices: pd.DataFrame = pd.DataFrame(), fraudulence = 0.05):
        """
            Initialize a bank

            @param name: The name of the bank
            @param locations: The locations for the simulation
            @param transactions: The transactions of the bank
            @param accounts: The bank accounts of the bank
            @param devices: The ATM devices of the bank
        """
        self.name = name
        self.transactions = transactions
        self.accounts = accounts
        self.devices = devices
        self.locations = locations
        self._lock = defaultdict(asyncio.Lock)
        self.fraudulence = fraudulence


    async def generate_device(self):
        """
            Generates a new bank device
            @return: A dictionary containing device information.
        """

        # Assign bank device a random location
        location = await random_location(self.locations)

        # Set a unique identifier for the device
        device_id = f"ATM_{self.name}_{uuid4()}"

        # Set device details
        device = {
            'device_id': device_id,
            'bank_name': self.name,
            **location
        }

        self.devices = pd.concat([self.devices, pd.DataFrame([device])])
        return device
    

    async def open_account(self, user: dict, kyc: int = None):
        """
            Opens a new bank account.
            @param user: The user data
            @param kyc: The kyc level of the account

            @return: A dictionary containing bank account information.
        """

        account_no = f"ACC_{(len(self.accounts) + 1):010}"

        # Set a random kyc level for account
        kyc = kyc if kyc is not None else random.choices([1, 2, 3], [.7, .19, .109], k=1)[0]

        # Set location for where this account is opened
        location = (
            {'latitude': user['latitude'], 'longitude': user['longitude']} 
            if random.random() > .3 
            else await random_location(self.locations, user['latitude'], user['longitude'])
        )

        # Set a random amount as the opening amount based on the account's kyc level
        opening_balance = generate_amount(kyc)

        # Select a random device for the user
        device = random.choice(user['devices'])

        # Initialize accout with basic information
        account = {
            'account_no': account_no,
            'account_name': user['name'],
            'balance': opening_balance,
            'kyc': kyc,
            'bvn': user['user_id'],
            'bank_name': self.name,
            'merchant': random.random() > 0.9,
            'opening_device': device
        }

        # Set the details for first transaction
        opening_transaction = {
            'amount': opening_balance,
            'balance': opening_balance,
            'time': global_clock.advance(5),
            'holder': account['account_no'],
            'holder_bank': account['bank_name'],
            'related': account['bank_name'],
            'related_bank': account['bank_name'],
            **location,
            'status': 'SUCCESS',
            'type': 'CREDIT',
            'category': 'OPENING',
            'channel': 'APP',
            'device': device,
            'reference': str(uuid4()),
            'reported': False
        }

        # Add opening transaction to the bank transactions
        await self.add_transaction(opening_transaction)

        # Add account to the account dataframe
        self.accounts = pd.concat([self.accounts, pd.DataFrame([account])])

        return account
    

    async def add_transaction(self, transaction):
        """
            Adds a transaction to the transactions dataframe
            @params transaction: The transaction to add
        """

        # Add transaction
        self.transactions = pd.concat([self.transactions, pd.DataFrame([transaction])], ignore_index=True)
        return transaction


    async def setup_devices(self, num_devices: int):
        """
            Setup the devices belonging to bank.
            @param num_devices: The number of ATM devices 

            @return: A DataFrame containing bank information.
        """
        devices = []

        # Initialize a random list of bank devices
        for _ in range(num_devices):
            device = await self.generate_device()

            # Add device to the general banks device list
            devices.append(device)

        # Store devices
        self.devices = pd.DataFrame(devices)
        return devices
    

    async def setup_accounts(self, users: list):
        """
            Setup the accounts belonging to bank.
            @param users: The users to open accounts for

            @return: A DataFrame containing bank accounts information.
        """
        accounts = []

        # Initialize a random list of bank accounts
        for user in users:
            account = await self.open_account(user)

            # Add account to the general banks account list
            accounts.append(account)

        # store accounts
        self.accounts = pd.DataFrame(accounts)
        return accounts
    

    async def setup(self, num_devices: int, users: list):
        """
            Setup the bank with devices and accounts.
            @param num_devices: The number of ATM devices 
            @param users: The users to open accounts for

            @return: None
        """

        # Setup bank devices
        await self.setup_devices(num_devices)

        # Setup bank accounts
        await self.setup_accounts(users)

    
    async def debit(self, account_no, related, related_bank, amount, device_id, location, category, channel, reference):
        """
            Debit an account

            @params account_no: The account the money is leaving
            @params related: The account the money is going to
            @params related_bank: The bank the money is going to
            @params amount: The amount to be debited
            @params device_id: The device used for the transaction
            @params location: The location of the transaction
            @params category: The category of the transaction
            @params channel: The channel used for the transaction
            @params reference: The reference of the transaction

            @return: The debit transaction details
        """

        # Deterine if the transaction will be successful, randomly. All reversals must be successful.
        async with self._lock[account_no]:
            status = 'SUCCESS' if category == 'REVERSAL' else random.choices(['SUCCESS', 'FAILED'], [0.7, 0.3], k=1)[0]
            account = self.accounts.loc[self.accounts['account_no'] == account_no].squeeze()

            # Get the balance of the transaction
            balance = round(account['balance'] - amount, 2) if status == 'SUCCESS' else account['balance']

            # Transaction fails if the balance is insufficient.
            if balance < 0:
                status = 'FAILED'
            else:
                # Update user account balance
                self.accounts.loc[self.accounts['account_no'] == account_no, 'balance'] = balance

            # Randomly report this transaction
            reported = random.random() < self.fraudulence  if status == 'SUCCESS' else False

            transaction = {
                'amount': amount,
                'balance': balance,
                'time': global_clock.advance(60),
                'holder': account_no,
                'holder_bank': account['bank_name'],
                'related': related,
                'related_bank': related_bank,
                **location,
                'channel': channel,
                'device': device_id,
                'status': status,
                'category': category,
                'type': 'DEBIT',
                'reference': reference,
                'reported': reported
            }

            # Save transaction
            await self.add_transaction(transaction)
            return transaction


    async def credit(self, account_no, related, related_bank, amount, device_id, location, category, channel, reference):
        """
            Credit an account

            @params account_no: The account the money is going to
            @params related: The account the money is leaving
            @params related_bank: The bank the money is going to
            @params device_id: The device used for the transaction
            @params location: The location of the transaction
            @params category: The category of the transaction
            @params channel: The channel used for the transaction
            @params reference: The reference of the transaction

            @return: The credit transaction details
        """
        async with self._lock[account_no]:
            account = self.accounts.loc[self.accounts['account_no'] == account_no].squeeze()

            # Get the balance of the transaction
            balance = round(account['balance'] + amount)

            # Update the account balance
            self.accounts.loc[self.accounts['account_no'] == account_no, 'balance'] = balance

            # Randomly report this transaction
            reported = random.random() < self.fraudulence

            transaction = {
                'amount': amount,
                'balance': balance,
                'time': global_clock.advance(60),
                'holder': account_no,
                'holder_bank': account['bank_name'],
                'related': related,
                'related_bank': related_bank,
                **location,
                'channel': channel,
                'device': device_id,
                'status': 'SUCCESS',
                'category': category,
                'type': 'CREDIT',
                'reference': reference,
                'reported': reported
            }

            await self.add_transaction(transaction)
            return transaction
