# model/train_model.py
"""
Train an IsolationForest model on collected 'normal' feature vectors.
Produces a model file model.pkl and a metadata file threshold.json for anomaly thresholds.
"""

import argparse
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DEFAULT_MODEL = "model.pkl"
DEFAULT_SCALER = "scaler.pkl"
DEFAULT_META = "model_meta.json"

def train(input_csv, out_model=DEFAULT_MODEL, out_scaler=DEFAULT_SCALER, out_meta=DEFAULT_META):
    df = pd.read_csv(input_csv)
    # drop non-feature cols if present
    drop_cols = [c for c in ['mac','time','label'] if c in df.columns]
    X = df.drop(columns=drop_cols).values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = IsolationForest(n_estimators=200, contamination=0.01, random_state=42)
    model.fit(Xs)

    # compute training scores (decision_function) and pick threshold (e.g. 1st percentile)
    scores = model.decision_function(Xs)
    threshold = float(np.percentile(scores, 2))  # tune this

    joblib.dump(model, out_model)
    joblib.dump(scaler, out_scaler)
    with open(out_meta, "w") as f:
        json.dump({"threshold": threshold, "feature_columns": list(df.drop(columns=drop_cols).columns)}, f)
    print(f"[+] Saved model -> {out_model}, scaler -> {out_scaler}, meta -> {out_meta}")
    print(f"[+] Training threshold score = {threshold}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV of normal feature vectors (one row per device window)")
    parser.add_argument("--out-model", default=DEFAULT_MODEL)
    parser.add_argument("--out-scaler", default=DEFAULT_SCALER)
    parser.add_argument("--out-meta", default=DEFAULT_META)
    args = parser.parse_args()
    train(args.input, args.out_model, args.out_scaler, args.out_meta)
