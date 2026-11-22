"""Score today's batches with the saved model and write alerts.

Usage (run daily after the load job, e.g. from Airflow/Control-M):
    python src/score_daily.py data/today.csv

Outputs:
    outputs/scored_today.csv   every batch + anomaly_score + flagged
    outputs/alerts.txt         human-readable alerts for flagged batches
Exit code 2 if any batch is flagged (so schedulers can branch on it).
"""
import pickle
import sys
import pandas as pd

MODEL_PATH = "models/pipeline_watch.pkl"

def score(csv_path):
    with open(MODEL_PATH, "rb") as f:
        b = pickle.load(f)
    df = pd.read_csv(csv_path)
    X = df[b["features"]].fillna(b["medians"]).to_numpy(float)
    Xs = b["scaler"].transform(X)
    df["anomaly_score"] = (-b["model"].decision_function(Xs)).round(4)
    df["flagged"] = (b["model"].predict(Xs) == -1).astype(int)
    import os
    os.makedirs("outputs", exist_ok=True)
    df.to_csv("outputs/scored_today.csv", index=False)

    med = b["medians"]
    lines = []
    for _, r in df[df["flagged"] == 1].iterrows():
        reasons = []
        if r["null_rate"] > med["null_rate"] * 5:
            reasons.append(f"null_rate {r['null_rate']:.3f} (normal ~{med['null_rate']:.3f})")
        if r["duplicate_rate"] > med["duplicate_rate"] * 5:
            reasons.append(f"duplicate_rate {r['duplicate_rate']:.3f} (normal ~{med['duplicate_rate']:.3f})")
        if r["row_count"] < med["row_count"] * 0.6:
            reasons.append(f"row_count {int(r['row_count'])} (normal ~{int(med['row_count'])})")
        if r["runtime_min"] > med["runtime_min"] * 2:
            reasons.append(f"runtime {r['runtime_min']:.0f} min (normal ~{med['runtime_min']:.0f})")
        if r["late_minutes"] > 60:
            reasons.append(f"late by {r['late_minutes']:.0f} min")
        why = "; ".join(reasons) if reasons else "unusual combination of metrics"
        lines.append(f"ALERT batch {r['batch_id']}: score {r['anomaly_score']:.3f} — {why}")
    with open("outputs/alerts.txt", "w") as f:
        f.write("\n".join(lines) if lines else "No anomalies today.\n")
    print("\n".join(lines) if lines else "No anomalies today.")
    return int(df["flagged"].sum())

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/today.csv"
    sys.exit(2 if score(path) else 0)
