import streamlit as st
import os
import joblib

from config.config import MODEL_DIR

def load_model(name = "predict_fraud_score_model_20250907_191011"):
    model_path = os.path.join(MODEL_DIR, name)
    return joblib.load(model_path)
