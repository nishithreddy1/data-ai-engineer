"""UC2 — Bad-record classification & data-quality scoring (supervised).

Classifies individual records as trustworthy vs suspect. Needs labelled
examples — in production these come from UC1's human review log.
Demo uses synthetic labelled records with realistic corruption patterns.
"""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(42)

def make_records(n=6000, bad_rate=0.12):
    n_bad = int(n * bad_rate); n_good = n - n_bad
    good = pd.DataFrame({
        "amount": rng.normal(1840, 320, n_good),
        "age_years": rng.integers(21, 75, n_good),
        "missing_fields": rng.integers(0, 2, n_good),
        "days_since_update": rng.integers(0, 30, n_good),
        "format_errors": rng.integers(0, 2, n_good),
        "duplicate_score": np.clip(rng.normal(0.05, 0.05, n_good), 0, 1),
        "is_bad": 0})
    bad = pd.DataFrame({
        "amount": rng.choice([-1, 0, 999999], n_bad) + rng.normal(0, 50, n_bad),
        "age_years": rng.choice([-5, 0, 150, 999], n_bad),
        "missing_fields": rng.integers(3, 9, n_bad),
        "days_since_update": rng.integers(180, 900, n_bad),
        "format_errors": rng.integers(2, 7, n_bad),
        "duplicate_score": np.clip(rng.normal(0.75, 0.15, n_bad), 0, 1),
        "is_bad": 1})
    return pd.concat([good, bad], ignore_index=True).sample(frac=1, random_state=1).reset_index(drop=True)

FEATS = ["amount", "age_years", "missing_fields", "days_since_update", "format_errors", "duplicate_score"]

def run():
    df = make_records()
    Xtr, Xte, ytr, yte = train_test_split(df[FEATS], df["is_bad"], test_size=0.25, random_state=42, stratify=df["is_bad"])
    models = {
        "LogisticRegression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "RandomForest": RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1),
    }
    results = []
    for name, model in models.items():
        model.fit(Xtr, ytr)
        pred = model.predict(Xte); proba = model.predict_proba(Xte)[:, 1]
        results.append({"model": name,
            "accuracy": round(float(accuracy_score(yte, pred)), 3),
            "precision": round(float(precision_score(yte, pred)), 3),
            "recall": round(float(recall_score(yte, pred)), 3),
            "f1": round(float(f1_score(yte, pred)), 3),
            "roc_auc": round(float(roc_auc_score(yte, proba)), 3)})
    best = max(results, key=lambda r: r["f1"])
    out = {"use_case": "2_bad_record_classification", "rows": int(len(df)),
           "bad_records": int(df.is_bad.sum()), "models": results, "best_by_f1": best["model"],
           "note": "Quality score = P(good) = 1 - P(bad); route low scores to review, never auto-delete."}
    json.dump(out, open("outputs/uc2_metrics.json", "w"), indent=2)
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
