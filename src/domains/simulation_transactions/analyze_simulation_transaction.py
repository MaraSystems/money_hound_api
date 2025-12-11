import pandas as pd

from src.domains.simulation_transactions.hound_transaction import hound_transaction
from src.domains.simulation_transactions.model import AnalyzedSimulationTransaction, SimulationTransaction
from src.lib.utils.lazycache import lazyload
from src.lib.utils.response import DataResponse


async def analyze_simulation_transaction(df: pd.DataFrame, accounts_df: pd.DataFrame):
    ...