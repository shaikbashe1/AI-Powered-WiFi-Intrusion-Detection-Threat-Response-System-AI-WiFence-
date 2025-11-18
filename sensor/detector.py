# detector/detector.py
"""
Detector service: reads captures.jsonl, builds features, loads model,
predicts anomalies and posts to controller endpoint.
"""

import time
import requests
import argparse
from processor.feature_builder import load_recent_events, build_device_features
from model.model_utils import load_model, predict_df
import pandas as pd

CONTROLLER_URL_DEFAULT = "http://localhost:8000/alert"

def main(model_path, scaler_path, meta_path, jsonl_path, controller_url, window_seconds=60, interval=10):
    model, scaler, meta = load_model(model_path, scaler_path, meta_path)
    print("[+] Detector started.")
    while True:
        df = load_recent_events(jsonl_path, window_seconds=window_seconds)
        feats = build_device_features(df)
        if feats.empty:
            time.sleep(interval)
            continue
        # ensure feature columns order
        for c in meta['feature_columns']:
            if c not in feats.columns:
                feats[c] = 0
        scores, labels = predict_df(feats, model, scaler, meta)
        for i, row in feats.reset_index(drop=True).iterrows():
            if labels[i] == -1:
                event = {
                    "mac": row["mac"],
                    "score": float(scores[i]),
                    "features": row[meta['feature_columns']].to_dict(),
                    "time": time.time()
                }
                try:
                    requests.post(controller_url, json=event, timeout=5)
                    print(f"[!] Alert posted for {row['mac']} score={scores[i]:.4f}")
                except Exception as e:
                    print(f"[!] Failed to post alert: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="model.pkl")
    parser.add_argument("--scaler", default="scaler.pkl")
    parser.add_argument("--meta", default="model_meta.json")
    parser.add_argument("--jsonl", default="captures.jsonl")
    parser.add_argument("--controller", default=CONTROLLER_URL_DEFAULT)
    parser.add_argument("--window", default=60, type=int)
    parser.add_argument("--interval", default=10, type=int)
    args = parser.parse_args()
    main(args.model, args.scaler, args.meta, args.jsonl, args.controller, args.window, args.interval)
