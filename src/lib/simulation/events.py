import pandas as pd
import random

from src.lib.simulation.banking import Bank
from src.lib.simulation.generator import random_account, random_atm, random_merchant, random_user_device
from src.lib.simulation.individual import Individual
from src.lib.simulation.generator import random_location


class Events:
    """
        Simulate banking events
    """

    def __init__(self, banks: dict, individuals: dict, locations: pd.DataFrame, fraudulence = 0.05):
        """
            Initialize events

            @param banks: The banks in the simulation
            @param individuals: The individuals in the simulation
            @param locations: The locations in the simulation
        """
        self.banks = banks
        self.individuals = individuals
        self.locations = locations
        self.fraudulence = fraudulence

        # define the event handlers and chance of occurance
        self.handler = {
            'ATM_WITHDRAWAL': self.atm_withdrawal,
            'ATM_DEPOSIT': self.atm_deposit,
            'ATM_PAYMENT': self.atm_payment,
            'POS_WITHDRAWAL': self.pos_withdrawal,
            'POS_PAYMENT': self.pos_payment,
            'MOBILE_TRANSFER': self.mobile_transfer,
            'TAKE_LOAN': self.take_loan
        }

    
    async def atm_withdrawal(self, holder, amount, reference, options: dict):
        """
            Simulates card withdrawal transactions

            @params holder: The details of the account the money is leaving
            @params amount: The amount to be credited
            @params reference: The reference of the transaction
            @params options: Abnormalities that can happen during this event
        """
        reverse = options.get('reverse', False)

        # Select a random bank device for this transaction
        bank_devices = pd.concat([bank.devices for bank in self.banks.values()])
        bank_device = await random_atm(bank_devices, holder['latitude'], holder['longitude'])

        # Get the device id
        device_id = bank_device['device_id']

        # Get the device location
        location = {
            'longitude': bank_device['longitude'],
            'latitude': bank_device['latitude']
        }

        # Set the related party of this transaction (The holder's bank)
        related = bank_device['account_no']
        related_bank = bank_device['bank_name']

        # Get the bank of the holder
        bank_of_holder: Bank = self.banks[holder['bank_name']]

        # Debit the holder and add transaction
        debit = await bank_of_holder.debit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='WITHDRAWAL', channel='CARD', reference=reference)

        # Balance the books if the transaction was a success
        if (debit['status'] == 'SUCCESS') and reverse:
            # Credit the related account and add the transaction
            await bank_of_holder.credit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='REVERSAL', channel='CARD', reference=reference)


    async def atm_deposit(self, holder, amount, reference, options: dict):
        """
            Simulates card deposit transactions

            @params holder: The details of the account the money is leaving
            @params amount: The amount to be credited
            @params reference: The reference of the transaction
            @params options: Abnormalities that can happen during this event
        """

        # Select a random bank device for this transaction
        bank_devices = pd.concat([bank.devices for bank in self.banks.values()])
        bank_device = await random_atm(bank_devices, holder['latitude'], holder['longitude'])

        # Get the device id
        device_id = bank_device['device_id']

        # Get the device location
        location = {
            'longitude': bank_device['longitude'],
            'latitude': bank_device['latitude']
        }

        # Set the related party of this transaction (The holder's bank)
        related = bank_device['account_no']
        related_bank = bank_device['bank_name']

        # Get the bank of the holder
        bank_of_holder: Bank = self.banks[holder['bank_name']]

        # Credit the holder and add transaction
        await bank_of_holder.credit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='DEPOSIT', channel='CARD', reference=reference)


    async def atm_payment(self, holder, amount, reference, options: dict):
        """
            Simulates card payment transactions

            @params holder: The details of the account the money is leaving
            @params amount: The amount to be credited
            @params reference: The reference of the transaction
            @params options: Abnormalities that can happen during this event
        """

        reverse = options.get('reverse', False)

        # Select a random bank device for this transaction
        bank_devices = pd.concat([bank.devices for bank in self.banks.values()])
        bank_device = await random_atm(bank_devices, holder['latitude'], holder['longitude'])

        # Get the device id
        device_id = bank_device['device_id']

        # Get the device location
        location = {
            'longitude': bank_device['longitude'],
            'latitude': bank_device['latitude']
        }

        # Select a random recipient account
        accounts = pd.concat([bank.accounts for bank in self.banks.values()])
        account = await random_account(accounts, exclude=holder['account_no'])

        # Set the relate account details
        related = account['account_no']
        related_bank = account['bank_name']

        # Get the bank of the holder
        bank_of_holder: Bank = self.banks[holder['bank_name']]

        # Get the bank of the related
        bank_of_related: Bank = self.banks[related_bank]

        # Set the category of the transaction randomly
        category = random.choice(['PAYMENT', 'BILL'])

        # Debit the holder and update the transactions dataframe
        debit = await bank_of_holder.debit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category=category, channel='CARD', reference=reference)

        # Was the transaction a success; balance the books.
        if (debit['status'] == 'SUCCESS'):
            # Credit the related account and update the transactions dataframe
            await bank_of_related.credit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category=category, channel='CARD', reference=reference)

            # For some reason a reveral was initiated.
            if reverse:
                # Reverse the debit and update transactions dataframe
                await bank_of_holder.credit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='REVERSAL', channel='CARD', reference=reference)

                # Reverse the credit and update transactions dataframe
                await bank_of_related.debit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category='REVERSAL', channel='CARD', reference=reference)


    async def pos_withdrawal(self, holder, amount, reference, options: dict):
        """
            Simulates card withdrawal transactions

            @params holder: The details of the account the money is leaving
            @params amount: The amount to be credited
            @params reference: The reference of the transaction
            @params options: Abnormalities that can happen during this event
        """
        reverse = options.get('reverse', False)

        # Select a random merchant for this transaction
        accounts = pd.concat([bank.accounts for bank in self.banks.values()])
        profiles = pd.DataFrame([individual.profile for individual in self.individuals.values()])
        merchant = await random_merchant(profiles, accounts, holder['latitude'], holder['longitude'])
        if merchant is None:
            return
        
        # Get the device id
        device_id = merchant['device_id']

        # Get the device location
        location = {
            'longitude': merchant['longitude'],
            'latitude': merchant['latitude']
        }

        # Set the related party of this transaction (The holder's bank)
        related = merchant['account_no']
        related_bank = merchant['bank_name']

        # Get the bank of the holder
        bank_of_holder: Bank = self.banks[holder['bank_name']]

        # Get the bank of the related
        bank_of_related: Bank = self.banks[related_bank]

        # Debit the holder and update the transactions dataframe
        debit = await bank_of_holder.debit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='WITHDRAWAL', channel='CARD', reference=reference)

        # Was the transaction a success; balance the books.
        if (debit['status'] == 'SUCCESS'):
            # Credit the related account and update the transactions dataframe
            await bank_of_related.credit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category='DEPOSIT', channel='CARD', reference=reference)

            # For some reason a reveral was initiated.
            if reverse:
                # Reverse the debit and update transactions dataframe
                await bank_of_holder.credit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='REVERSAL', channel='CARD', reference=reference)

                # Reverse the credit and update transactions dataframe
                await bank_of_related.debit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category='REVERSAL', channel='CARD', reference=reference)


    async def pos_payment(self, holder, amount, reference, options: dict):
        """
            Simulates card payment transactions

            @params holder: The details of the account the money is leaving
            @params amount: The amount to be credited
            @params reference: The reference of the transaction
            @params options: Abnormalities that can happen during this event
        """
        reverse = options.get('reverse', False)

        # Select a random merchant for this transaction
        accounts = pd.concat([bank.accounts for bank in self.banks.values()])
        profiles = pd.DataFrame([individual.profile for individual in self.individuals.values()])
        merchant = await random_merchant(profiles, accounts, holder['latitude'], holder['longitude'])

        if merchant is None:
            return

        # Get the device id
        device_id = merchant['device_id']

        # Get the device location
        location = {
            'longitude': merchant['longitude'],
            'latitude': merchant['latitude']
        }

        # Set the related party of this transaction (The holder's bank)
        related = merchant['account_no']
        related_bank = merchant['bank_name']

        # Get the bank of the holder
        bank_of_holder: Bank = self.banks[holder['bank_name']]

        # Get the bank of the related
        bank_of_related: Bank = self.banks[related_bank]

        # Set the category of the transaction randomly
        category = random.choice(['PAYMENT', 'BILL'])

        # Debit the holder and update the transactions dataframe
        debit = await bank_of_holder.debit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category=category, channel='CARD', reference=reference)

        # Was the transaction a success; balance the books.
        if (debit['status'] == 'SUCCESS'):
            # Credit the related account and update the transactions dataframe
            await bank_of_related.credit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category=category, channel='CARD', reference=reference)

            # For some reason a reveral was initiated.
            if reverse:
                # Reverse the debit and update transactions dataframe
                await bank_of_holder.credit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='REVERSAL', channel='CARD', reference=reference)

                # Reverse the credit and update transactions dataframe
                await bank_of_related.debit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category='REVERSAL', channel='CARD', reference=reference)


    async def mobile_transfer(self, holder, amount, reference, options: dict):
        """
            Simulates mobile transfer transactions

            @params holder: The details of the account the money is leaving
            @params amount: The amount to be credited
            @params reference: The reference of the transaction
            @params options: Abnormalities that can happen during this event
        """
        reverse = options.get('reverse', False)

        # Get the user's BVN
        individual: Individual = self.individuals[holder['bvn']]

        # Select a random device belonging to the user or a random device
        device_id = random.choice(individual.profile['devices']) if random.random() >= .95 else await random_user_device(self.individuals)

        # Set a location for the transaction (Randomly or User's Location)
        location = await random_location(self.locations, holder['latitude'], holder['longitude'])

        # Select a random recipient account
        accounts = pd.concat([bank.accounts for bank in self.banks.values()])
        account = await random_account(accounts, exclude=holder['account_no'])

        # Set the relate account details
        related = account['account_no']
        related_bank = account['bank_name']

        # Get the bank of the holder
        bank_of_holder: Bank = self.banks[holder['bank_name']]

        # Get the bank of the related
        bank_of_related: Bank = self.banks[related_bank]

        # Set the channel of the transaction randomly
        channel = random.choices(['APP', 'USSD'], [3, 1], k=1)[0]

        # Debit the holder and update the transactions dataframe
        debit = await bank_of_holder.debit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='TRANSFER', channel=channel, reference=reference)

        # Was the transaction a success; balance the books.
        if (debit['status'] == 'SUCCESS'):
            # Credit the related account and update the transactions dataframe
            await bank_of_related.credit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category='TRANSFER', channel=channel, reference=reference)

            # For some reason a reveral was initiated.
            if reverse:
                # Reverse the debit and update transactions dataframe
                await bank_of_holder.credit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='REVERSAL', channel=channel, reference=reference)

                # Reverse the credit and update transactions dataframe
                await bank_of_related.debit(account_no=related, related=holder['account_no'], related_bank=holder['bank_name'], amount=amount, device_id=device_id, location=location, category='REVERSAL', channel=channel, reference=reference)


    async def take_loan(self, holder, amount, reference, options: dict):
        """
            Simulates loan transactions
            
            @params holder: The details of the account the money is leaving
            @params amount: The amount to be credited
            @params reference: The reference of the transaction
            @params options: Abnormalities that can happen during this event
        """

        # Get the user's BVN
        individual: Individual = self.individuals[holder['bvn']]

        # Select a random device belonging to the user or a random device
        device_id = random.choice(individual.profile['devices']) if random.random() >= .95 else await random_user_device(self.individuals)

        # Set a location for the transaction (Randomly or User's Location)
        location = await random_location(self.locations, holder['latitude'], holder['longitude'])

        # Select the bank for the account
        accounts = pd.concat([bank.accounts for bank in self.banks.values()])
        account = accounts.loc[(accounts['account_no'] == holder['account_no']) & (accounts['bank_name'] == holder['bank_name'])].squeeze()

        # Set the relate account details
        related = account['account_no']
        related_bank = account['bank_name']

        # Select a random channel for the transaction
        channel = random.choices(['APP', 'USSD'], [3, 1], k=1)[0]

        # Get the bank of the holder
        bank_of_holder: Bank = self.banks[holder['bank_name']]

        # Credit the holder and update the transactions dataframe
        await bank_of_holder.credit(account_no=holder['account_no'], related=related, related_bank=related_bank, amount=amount, device_id=device_id, location=location, category='LOAN', channel=channel, reference=reference)


    async def spin(self, individual: Individual):
        """
            Simulates an event occurring in the banking process
        """

        events = list(self.handler.keys())
        chances = [individual.behaviour[e] for e in events]

        # # Selects a random event based on occurance rates
        event_name = random.choices(
            events,
            chances,
            k=1
        )[0]

        return self.handler[event_name]