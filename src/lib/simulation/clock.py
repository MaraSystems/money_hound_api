import random
from datetime import timedelta, datetime


class SyntheticClock:
    """
        A synthetic clock class to manage time ticking.
    """

    def __init__(self, basetime: datetime):
        """
            Initializes the synthetic clock.

            @param base_time: The base time to start ticking from.
        """
        self.basetime = basetime
        self.ticker = 0


    def advance(self, sec=1):
        """
            A synthetic clock ticker.

            @param sec: The number of seconds to tick forward.

            @return: The current time after ticking forward.
        """

        # Pick a random number of seconds
        self.ticker += random.randint(0, sec)

        # Update the base time using the selected number of seconds
        time = self.basetime + timedelta(seconds=self.ticker)
        return time.isoformat()
    

    def now(self):
        """
            Returns the current time of the synthetic clock.

            @return: The current time.
        """
        return self.basetime + timedelta(seconds=self.ticker)
    

    def reset(self, basetime = datetime(2023, 1, 1, 0, 0, 0)):
        """
            Resets the synthetic clock to a new base time.

            @param base_time: The new base time to reset to.
        """
        self.basetime = basetime
        self.ticker = 0


global_clock = SyntheticClock(datetime(2023, 1, 1, 0, 0, 0))