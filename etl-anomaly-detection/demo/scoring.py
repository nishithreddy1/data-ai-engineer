"""Pipeline Watch scoring core — unsupervised ETL batch anomaly detection.

Same method as the verified ml-for-data-engineering experiment
(src/detect.py): Isolation Forest on per-batch metrics, labels used ONLY
for evaluation when present, never for training.
"""
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             precision_score, recall_score, roc_auc_score)
from sklearn.preprocessing import StandardScaler

FEATURES = ["day_of_week", "row_count", "null_rate", "duplicate_rate",
            "reject_rate", "avg_amount", "distinct_keys_ratio",
            "runtime_min", "late_minutes"]


def score_batches(df, contamination=0.05, seed=42):
    """Score every batch. Returns (scored_df, metrics_or_None).

    metrics is None when the input has no `is_anomaly` label column
    (the real-world case: you score first, review flagged batches).
    """
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    X = df[FEATURES].to_numpy(float)
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    model = IsolationForest(n_estimators=300, contamination=contamination,
                            random_state=seed, n_jobs=-1).fit(Xs)
    scores = -model.decision_function(Xs)          # higher = more anomalous
    pred = (model.predict(Xs) == -1).astype(int)   # 1 = flagged for review

    out = df.copy()
    out["anomaly_score"] = scores.round(4)
    out["flagged"] = pred
    out = out.sort_values("anomaly_score", ascending=False)

    metrics = None
    if "is_anomaly" in df.columns:
        y = df["is_anomaly"].to_numpy(int)
        metrics = {
            "rows": int(len(df)),
            "planted_anomalies": int(y.sum()),
            "flagged": int(pred.sum()),
            "precision": round(float(precision_score(y, pred, zero_division=0)), 3),
            "recall": round(float(recall_score(y, pred, zero_division=0)), 3),
            "roc_auc": round(float(roc_auc_score(y, scores)), 3),
            "pr_auc": round(float(average_precision_score(y, scores)), 3),
            "confusion_matrix": confusion_matrix(y, pred).tolist(),
            "contamination": contamination,
        }
    return out, metrics
