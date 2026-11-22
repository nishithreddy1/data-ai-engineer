"""Train Pipeline Watch on historical batch metrics and save the model.

Usage:
    python src/train.py data/history.csv [contamination]

Input: CSV from the collector (batch_id + 9 metric columns), 3-6 months.
Saves: models/pipeline_watch.pkl (scaler + model + feature medians + threshold)
"""
import json
import pickle
import sys
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURES = ["day_of_week", "row_count", "null_rate", "duplicate_rate",
            "reject_rate", "avg_amount", "distinct_keys_ratio",
            "runtime_min", "late_minutes"]

def train(csv_path, contamination=0.03, seed=42, model_path="models/pipeline_watch.pkl"):
    df = pd.read_csv(csv_path)
    medians = df[FEATURES].median()
    X = df[FEATURES].fillna(medians).to_numpy(float)
    scaler = StandardScaler().fit(X)
    model = IsolationForest(n_estimators=300, contamination=contamination,
                            random_state=seed, n_jobs=-1).fit(scaler.transform(X))
    bundle = {"scaler": scaler, "model": model, "medians": medians,
              "features": FEATURES, "contamination": contamination,
              "trained_rows": int(len(df))}
    import os
    os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(bundle, f)
    flagged = int((model.predict(scaler.transform(X)) == -1).sum())
    print(json.dumps({"trained_rows": len(df), "flagged_in_history": flagged,
                      "contamination": contamination, "model": model_path}, indent=2))
    return bundle

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/history.csv"
    cont = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
    train(path, cont)
