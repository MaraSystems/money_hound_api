import random
import pandas as pd
from uuid import uuid4

from src.lib.simulation.generator import random_location
from src.lib.simulation.generator import fake


class Individual:
    """
        Simulate an individual actions
    """

    def __init__(self, locations: pd.DataFrame, profile: dict = {}, behaviour = {}):
        """
            Initialize an individual

            @param profile: The profile of the individual
        """
        self.locations = locations
        self.profile = profile
        self.behaviour = behaviour


    async def setup_profile(self) -> dict:
        """
            Setup the profile of an individual
        """

        # Set the unique identifier for each user
        user_id = f"USER_{uuid4()}"
        profile = fake.profile()

        # Assign user a random number of devices
        num_devices = random.randint(1, 2)

        # Assign user a random location
        location = await random_location(self.locations)

        # Initialize an empty device list to this user
        user_devices = []

        # Generate devices for each user
        for _ in range(num_devices):
            # Set a unique identifier for the device
            device_id = f"{'MOBILE'}_{user_id}_{uuid4()}"

            # Add device to the specific user device list
            user_devices.append(device_id)

        # Add user to the user list
        self.profile = {
            'user_id': user_id,
            'devices': user_devices,
            'name': profile['name'],
            'gender': profile['sex'],
            'email': profile['mail'],
            'birthdate': profile['birthdate'].isoformat(),
            **location
        }


    async def setup_behaviour(self):
        """
            Setup the behaviors of an individual
        """

        events = ['ATM_WITHDRAWAL', 'ATM_DEPOSIT', 'ATM_PAYMENT', 'POS_WITHDRAWAL', 'POS_PAYMENT', 'MOBILE_TRANSFER', 'TAKE_LOAN']
        occurances = [1, 1, 2, 3, 3, 7, 3]
        self.behaviour = {e:random.randint(0, occurances[i]) for i, e in enumerate(events)}


    async def setup(self):
        """
            Setup an individual
        """

        await self.setup_profile()

        await self.setup_behaviour()
