"""UC5 — Sequence anomaly detection (autoencoder-style reconstruction).

Models a daily metric (e.g. load volume) over time: a slow drift no single
batch reveals still triggers. Uses an MLP autoencoder (scikit-learn) on
rolling windows — same idea as an LSTM autoencoder, lighter to run.
Score = reconstruction error; threshold from normal-period errors.
"""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(42)
WINDOW = 14

def make_series(days=365):
    t = np.arange(days)
    weekly = 1 - 0.35 * np.isin(t % 7, [5, 6])
    volume = 52000 * weekly + rng.normal(0, 1800, days)
    truth = np.zeros(days, dtype=int)
    # slow drift: days 250-290 sag 35%; spike: days 320-322 collapse
    volume[250:290] *= np.linspace(1.0, 0.65, 40); truth[270:290] = 1
    volume[320:323] *= 0.3; truth[320:323] = 1
    return volume, truth

def windows(x):
    return np.array([x[i:i + WINDOW] for i in range(len(x) - WINDOW)])

def run():
    volume, truth = make_series()
    scaler = StandardScaler().fit(volume[:200].reshape(-1, 1))  # normal period only
    xs = scaler.transform(volume.reshape(-1, 1)).ravel()
    X = windows(xs)
    ae = MLPRegressor(hidden_layer_sizes=(8,), activation="relu", max_iter=800,
                      random_state=42).fit(X[:186], X[:186])  # train on normal windows
    err = ((X - ae.predict(X)) ** 2).mean(axis=1)
    thresh = np.quantile(err[:186], 0.97)
    flagged = (err > thresh).astype(int)
    y = truth[WINDOW:]
    out = {"use_case": "5_sequence_anomaly_autoencoder", "days": int(len(volume)),
           "window_days": WINDOW, "threshold_q97_normal": round(float(thresh), 4),
           "precision": round(float(precision_score(y, flagged, zero_division=0)), 3),
           "recall": round(float(recall_score(y, flagged, zero_division=0)), 3),
           "roc_auc": round(float(roc_auc_score(y, err)), 3),
           "note": "Catches slow drift + collapses; explanations weaker than UC1 — pair both."}
    pd.DataFrame({"day": range(WINDOW, len(volume)), "volume": volume[WINDOW:],
                  "recon_error": err.round(4), "flagged": flagged, "is_anomaly": y}).to_csv(
        "outputs/uc5_scored_series.csv", index=False)
    json.dump(out, open("outputs/uc5_metrics.json", "w"), indent=2)
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
