"""UC3 — Pipeline failure & SLA-breach prediction (supervised, from run history).

Predicts which jobs will fail or breach their SLA window so you intervene
before the breach. Needs labelled run history (Control-M/Airflow logs).
Demo uses synthetic run history with realistic risk drivers.
"""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(42)

def make_runs(n=4000):
    df = pd.DataFrame({
        "input_rows_m": np.clip(rng.normal(2.4, 0.9, n), 0.1, None),
        "prev_failures_7d": rng.poisson(0.6, n),
        "avg_runtime_min": np.clip(rng.normal(42, 12, n), 5, None),
        "runtime_trend": rng.normal(0, 0.08, n),
        "upstream_late_min": np.clip(rng.normal(6, 9, n), 0, None),
        "day_of_week": rng.integers(0, 7, n),
        "concurrent_jobs": rng.integers(1, 12, n),
        "days_since_change": rng.integers(0, 90, n),
    })
    logit = (-3.2 + 0.9 * df["prev_failures_7d"] + 2.2 * df["runtime_trend"]
             + 0.03 * df["upstream_late_min"] + 0.12 * df["concurrent_jobs"]
             + np.where(df["days_since_change"] < 3, 1.1, 0))
    p = 1 / (1 + np.exp(-logit))
    df["will_breach"] = (rng.random(n) < p).astype(int)
    return df

FEATS = ["input_rows_m", "prev_failures_7d", "avg_runtime_min", "runtime_trend",
         "upstream_late_min", "day_of_week", "concurrent_jobs", "days_since_change"]

def run():
    df = make_runs()
    Xtr, Xte, ytr, yte = train_test_split(df[FEATS], df["will_breach"], test_size=0.25, random_state=42, stratify=df["will_breach"])
    model = GradientBoostingClassifier(random_state=42).fit(Xtr, ytr)
    proba = model.predict_proba(Xte)[:, 1]
    pred = (proba >= 0.5).astype(int)
    importance = sorted(zip(FEATS, model.feature_importances_.round(3)), key=lambda t: -t[1])
    out = {"use_case": "3_sla_failure_prediction", "runs": int(len(df)),
           "breach_rate": round(float(df.will_breach.mean()), 3),
           "precision": round(float(precision_score(yte, pred)), 3),
           "recall": round(float(recall_score(yte, pred)), 3),
           "roc_auc": round(float(roc_auc_score(yte, proba)), 3),
           "top_risk_drivers": [{"feature": f, "importance": float(v)} for f, v in importance[:4]],
           "note": "Alert on P(breach) > threshold; tune threshold to on-call budget."}
    json.dump(out, open("outputs/uc3_metrics.json", "w"), indent=2)
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
