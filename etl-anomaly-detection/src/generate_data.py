"""Generate synthetic ETL batch data with planted anomalies (labelled, for evaluation only).

Simulates a daily Teradata/DataStage-style load: one row per batch file with
volume, quality and performance metrics. Normal rows follow stable patterns;
anomaly rows inject realistic failures (volume drop, null spike, duplicate
surge, late arrival, runtime blowout). Synthetic only — no real records.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

def make_batches(n_normal=1900, n_anomaly=100):
    # --- normal batches ---
    dow = rng.integers(0, 7, n_normal)
    weekend = np.isin(dow, [5, 6]).astype(float)
    base_volume = rng.normal(52000, 4200, n_normal) * (1 - 0.35 * weekend)
    normal = pd.DataFrame({
        "day_of_week": dow,
        "row_count": base_volume.round().astype(int),
        "null_rate": np.clip(rng.normal(0.008, 0.003, n_normal), 0, 1),
        "duplicate_rate": np.clip(rng.normal(0.004, 0.002, n_normal), 0, 1),
        "reject_rate": np.clip(rng.normal(0.006, 0.003, n_normal), 0, 1),
        "avg_amount": rng.normal(1840, 160, n_normal),
        "distinct_keys_ratio": np.clip(rng.normal(0.92, 0.02, n_normal), 0, 1),
        "runtime_min": np.clip(base_volume / 52000 * rng.normal(38, 4, n_normal), 5, None),
        "late_minutes": np.clip(rng.normal(4, 3, n_normal), 0, None),
        "is_anomaly": 0,
    })
    # --- anomalous batches: pick a failure mode per row ---
    modes = rng.choice(["volume_drop", "null_spike", "dup_surge", "late", "runtime"], n_anomaly)
    anom = normal.sample(n_anomaly, replace=True, random_state=7).copy().reset_index(drop=True)
    anom["is_anomaly"] = 1
    for i, (idx, mode) in enumerate(zip(anom.index, modes)):
        if mode == "volume_drop":
            anom.loc[idx, "row_count"] = int(anom.loc[idx, "row_count"] * rng.uniform(0.15, 0.45))
        elif mode == "null_spike":
            anom.loc[idx, "null_rate"] = rng.uniform(0.18, 0.55)
            anom.loc[idx, "reject_rate"] = rng.uniform(0.10, 0.35)
        elif mode == "dup_surge":
            anom.loc[idx, "duplicate_rate"] = rng.uniform(0.15, 0.45)
            anom.loc[idx, "distinct_keys_ratio"] = rng.uniform(0.35, 0.6)
        elif mode == "late":
            anom.loc[idx, "late_minutes"] = rng.uniform(120, 600)
        elif mode == "runtime":
            anom.loc[idx, "runtime_min"] = anom.loc[idx, "runtime_min"] * rng.uniform(2.5, 4.5)
    df = pd.concat([normal, anom], ignore_index=True).sample(frac=1, random_state=1).reset_index(drop=True)
    df.insert(0, "batch_id", [f"B{100000+i}" for i in range(len(df))])
    return df

if __name__ == "__main__":
    df = make_batches()
    df.to_csv("data/etl_batches.csv", index=False)
    print(df.shape, "anomalies:", int(df.is_anomaly.sum()))
    print(df.head(3).to_string())
