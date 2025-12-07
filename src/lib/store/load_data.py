import pandas as pd
import kagglehub
import os

from src.config.config import ENV, DATA_URL, DATA_DIR

def download_data(name: str):
    path = kagglehub.dataset_download(DATA_URL)
    return path


def load_data(file, parse_dates=None):
    file_path = os.path.join(DATA_DIR, file)

    if ENV == 'production':
        path = download_data(file)
        file_path = os.path.join(path, file)

    if parse_dates:
        df = pd.read_csv(file_path, parse_dates=parse_dates)
    else:
        df = pd.read_csv(file_path)
    return df