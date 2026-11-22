"""Score REAL batches with Isolation Forest (no labels needed).

Usage:
    python detect_real.py path/to/batch_metrics.csv [contamination]

Input CSV columns: batch_id, day_of_week, row_count, null_rate,
duplicate_rate, reject_rate, avg_amount, distinct_keys_ratio,
runtime_min, late_minutes   (produced by the PySpark / Teradata collectors)

Output: outputs/scored_batches.csv sorted by anomaly_score (highest first).
Review the top rows manually for the first weeks; tune `contamination`
(the share of batches you expect to be bad, e.g. 0.02-0.05) to your alert budget.
"""
import json
import sys
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURES = ["day_of_week", "row_count", "null_rate", "duplicate_rate",
            "reject_rate", "avg_amount", "distinct_keys_ratio",
            "runtime_min", "late_minutes"]

def run(csv_path, contamination=0.03, seed=42):
    df = pd.read_csv(csv_path)
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns: {missing}")
    X = df[FEATURES].fillna(df[FEATURES].median()).to_numpy(float)
    Xs = StandardScaler().fit_transform(X)
    model = IsolationForest(n_estimators=300, contamination=contamination,
                            random_state=seed, n_jobs=-1).fit(Xs)
    out = df.copy()
    out["anomaly_score"] = (-model.decision_function(Xs)).round(4)
    out["flagged"] = (model.predict(Xs) == -1).astype(int)
    import os
    os.makedirs("outputs", exist_ok=True)
    out.sort_values("anomaly_score", ascending=False).to_csv(
        "outputs/scored_batches.csv", index=False)
    summary = {"rows": int(len(df)), "flagged": int(out["flagged"].sum()),
               "contamination": contamination}
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/batch_metrics.csv"
    cont = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
    run(path, cont)
