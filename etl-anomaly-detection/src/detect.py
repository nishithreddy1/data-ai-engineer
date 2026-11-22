"""Detect anomalous ETL batches with Isolation Forest (unsupervised).

Why unsupervised: in real pipelines you rarely have labelled failures.
The model learns 'normal' batch behaviour and scores deviations.
Labels in the synthetic file are used ONLY to evaluate, never to train.
"""
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             precision_score, recall_score, roc_auc_score)
from sklearn.preprocessing import StandardScaler

FEATURES = ["day_of_week", "row_count", "null_rate", "duplicate_rate",
            "reject_rate", "avg_amount", "distinct_keys_ratio",
            "runtime_min", "late_minutes"]

def run(csv_path="data/etl_batches.csv", contamination=0.05, seed=42):
    df = pd.read_csv(csv_path)
    X = df[FEATURES].to_numpy(float)
    y = df["is_anomaly"].to_numpy(int)
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    model = IsolationForest(n_estimators=300, contamination=contamination,
                            random_state=seed, n_jobs=-1).fit(Xs)
    scores = -model.decision_function(Xs)          # higher = more anomalous
    pred = (model.predict(Xs) == -1).astype(int)   # 1 = flagged
    metrics = {
        "rows": int(len(df)), "planted_anomalies": int(y.sum()),
        "flagged": int(pred.sum()),
        "precision": round(float(precision_score(y, pred, zero_division=0)), 3),
        "recall": round(float(recall_score(y, pred, zero_division=0)), 3),
        "roc_auc": round(float(roc_auc_score(y, scores)), 3),
        "pr_auc": round(float(average_precision_score(y, scores)), 3),
        "confusion_matrix": confusion_matrix(y, pred).tolist(),
        "contamination": contamination,
    }
    out = df.copy()
    out["anomaly_score"] = scores.round(4)
    out["flagged"] = pred
    out.sort_values("anomaly_score", ascending=False).to_csv(
        "outputs/scored_batches.csv", index=False)
    with open("outputs/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    return metrics

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
