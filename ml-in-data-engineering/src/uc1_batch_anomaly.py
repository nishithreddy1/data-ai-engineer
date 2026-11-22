"""UC1 — Batch anomaly detection (Isolation Forest + LOF + One-Class SVM comparison).

Scores every ETL load on operational metrics; flags outliers for human review.
Unsupervised: learns normal behaviour, no labels needed for training.
Labels in synthetic data are used only for evaluation.
"""
import json
import numpy as np
import pandas as pd
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

rng = np.random.default_rng(42)

def make_data(n_normal=1900, n_anomaly=100):
    dow = rng.integers(0, 7, n_normal)
    wknd = np.isin(dow, [5, 6]).astype(float)
    vol = rng.normal(52000, 4200, n_normal) * (1 - 0.35 * wknd)
    df = pd.DataFrame({
        "day_of_week": dow, "row_count": vol.round().astype(int),
        "null_rate": np.clip(rng.normal(0.008, 0.003, n_normal), 0, 1),
        "duplicate_rate": np.clip(rng.normal(0.004, 0.002, n_normal), 0, 1),
        "reject_rate": np.clip(rng.normal(0.006, 0.003, n_normal), 0, 1),
        "avg_amount": rng.normal(1840, 160, n_normal),
        "distinct_keys_ratio": np.clip(rng.normal(0.92, 0.02, n_normal), 0, 1),
        "runtime_min": np.clip(vol / 52000 * rng.normal(38, 4, n_normal), 5, None),
        "late_minutes": np.clip(rng.normal(4, 3, n_normal), 0, None),
        "is_anomaly": 0})
    modes = rng.choice(["volume_drop", "null_spike", "dup_surge", "late", "runtime"], n_anomaly)
    anom = df.sample(n_anomaly, replace=True, random_state=7).copy().reset_index(drop=True)
    anom["is_anomaly"] = 1
    for idx, mode in zip(anom.index, modes):
        if mode == "volume_drop": anom.loc[idx, "row_count"] = int(anom.loc[idx, "row_count"] * rng.uniform(0.15, 0.45))
        elif mode == "null_spike":
            anom.loc[idx, "null_rate"] = rng.uniform(0.18, 0.55); anom.loc[idx, "reject_rate"] = rng.uniform(0.10, 0.35)
        elif mode == "dup_surge":
            anom.loc[idx, "duplicate_rate"] = rng.uniform(0.15, 0.45); anom.loc[idx, "distinct_keys_ratio"] = rng.uniform(0.35, 0.6)
        elif mode == "late": anom.loc[idx, "late_minutes"] = rng.uniform(120, 600)
        else: anom.loc[idx, "runtime_min"] = anom.loc[idx, "runtime_min"] * rng.uniform(2.5, 4.5)
    return pd.concat([df, anom], ignore_index=True).sample(frac=1, random_state=1).reset_index(drop=True)

FEATS = ["day_of_week","row_count","null_rate","duplicate_rate","reject_rate",
         "avg_amount","distinct_keys_ratio","runtime_min","late_minutes"]

def evaluate(name, scores, y, flagged):
    return {"model": name,
            "precision": round(float(precision_score(y, flagged, zero_division=0)), 3),
            "recall": round(float(recall_score(y, flagged, zero_division=0)), 3),
            "roc_auc": round(float(roc_auc_score(y, scores)), 3),
            "flagged": int(flagged.sum())}

def run():
    df = make_data()
    X = StandardScaler().fit_transform(df[FEATS].to_numpy(float))
    y = df["is_anomaly"].to_numpy(int)
    results = []
    m = IsolationForest(n_estimators=300, contamination=0.05, random_state=42, n_jobs=-1).fit(X)
    results.append(evaluate("IsolationForest", -m.decision_function(X), y, (m.predict(X) == -1).astype(int)))
    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
    pred = lof.fit_predict(X)
    results.append(evaluate("LocalOutlierFactor", -lof.negative_outlier_factor_, y, (pred == -1).astype(int)))
    svm = OneClassSVM(nu=0.05, kernel="rbf", gamma="scale").fit(X)
    results.append(evaluate("OneClassSVM", -svm.decision_function(X), y, (svm.predict(X) == -1).astype(int)))
    best = max(results, key=lambda r: r["roc_auc"])
    out = {"use_case": "1_batch_anomaly_detection", "rows": int(len(df)),
           "planted_anomalies": int(y.sum()), "models": results, "best_by_roc_auc": best["model"]}
    df.assign(anomaly_score=(-m.decision_function(X)).round(4)).sort_values(
        "anomaly_score", ascending=False).to_csv("outputs/uc1_scored_batches.csv", index=False)
    json.dump(out, open("outputs/uc1_metrics.json", "w"), indent=2)
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
