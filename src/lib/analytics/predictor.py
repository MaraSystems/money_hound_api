import streamlit as st
import random
import numpy as np
import pandas as pd

from ..store.load_model import load_model
from .unusual import unusual


def predict(data):
    np.random.seed(42)
    unusual_data = unusual(data)
    
    st.subheader('Summary')
    data = unusual_data.drop(columns=['fraud', 'fraud_score'])

    model = load_model()
    pred = model.predict(data)

    classified = unusual_data.iloc[0]

    result = {
        'Fraudulent': classified['fraud'],
        'Fraud Score': "{:.3g}".format(classified['fraud_score']),
        'Predicted Score': "{:.3g}".format(pred[0])
    }
    st.table(result)
    return result
