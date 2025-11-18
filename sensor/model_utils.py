# model/model_utils.py
import joblib
import json
import numpy as np
import pandas as pd

def load_model(model_path="model.pkl", scaler_path="scaler.pkl", meta_path="model_meta.json"):
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    with open(meta_path, "r") as f:
        meta = json.load(f)
    return model, scaler, meta

def predict_df(feat_df, model, scaler, meta):
    """
    feat_df: pandas DataFrame with rows matching meta['feature_columns']
    returns: scores (decision_function), labels (-1 anomaly, 1 normal)
    """
    cols = meta["feature_columns"]
    X = feat_df[cols].values
    Xs = scaler.transform(X)
    scores = model.decision_function(Xs)
    labels = model.predict(Xs)
    return scores, labels
