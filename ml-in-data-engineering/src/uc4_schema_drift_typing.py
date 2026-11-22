"""UC4 — Schema drift detection + semantic typing (lightweight, no deep net).

Full Sherlock/Sato-style models need 1,500+ features and training corpora.
This demo does the practical 80%: (a) infer each column's semantic type from
value patterns, (b) detect drift between two snapshots with PSI (Population
Stability Index) + schema diff. Swap in a trained classifier later.
"""
import json
import re
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

PATTERNS = {
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "date_iso": re.compile(r"^\d{4}-\d{2}-\d{2}"),
    "phone": re.compile(r"^\+?[\d\s\-]{10,15}$"),
    "gstin_like": re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$"),
    "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I),
}

def infer_type(series: pd.Series) -> str:
    s = series.dropna().astype(str).head(500)
    if len(s) == 0: return "empty"
    for name, pat in PATTERNS.items():
        if s.str.match(pat).mean() > 0.9: return name
    numeric = pd.to_numeric(s, errors="coerce")
    if numeric.notna().mean() > 0.95:
        return "integer" if (numeric.dropna() % 1 == 0).all() else "decimal"
    if s.nunique() <= max(20, len(s) * 0.05): return "categorical"
    return "free_text"

def psi(expected: np.ndarray, actual: np.ndarray, bins=10) -> float:
    qs = np.quantile(expected, np.linspace(0, 1, bins + 1)); qs[0], qs[-1] = -np.inf, np.inf
    e = np.histogram(expected, qs)[0] / len(expected)
    a = np.histogram(actual, qs)[0] / len(actual)
    e, a = np.clip(e, 1e-6, None), np.clip(a, 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))

def snapshot(n, drift=False):
    return pd.DataFrame({
        "customer_id": [f"C{i:06d}" for i in range(n)],
        "email": [f"user{i}@example.com" for i in range(n)],
        "amount": rng.normal(2400 if drift else 1840, 320, n),          # drifted mean
        "country": rng.choice(["IN", "AE", "SG"] if drift else ["IN", "AE"], n),
        "txn_date": pd.date_range("2026-01-01", periods=n, freq="h").strftime("%Y-%m-%d"),
        **({"new_risk_flag": rng.choice(["Y", "N"], n)} if drift else {}),  # new column
    })

def run():
    base, cur = snapshot(3000), snapshot(3000, drift=True)
    types = {c: infer_type(base[c]) for c in base.columns}
    added = sorted(set(cur.columns) - set(base.columns))
    removed = sorted(set(base.columns) - set(cur.columns))
    drift = {}
    for c in set(base.columns) & set(cur.columns):
        if pd.api.types.is_numeric_dtype(base[c]):
            v = round(psi(base[c].to_numpy(float), cur[c].to_numpy(float)), 3)
            drift[c] = {"psi": v, "verdict": "major drift" if v > 0.25 else "moderate" if v > 0.1 else "stable"}
    out = {"use_case": "4_schema_drift_semantic_typing", "inferred_types": types,
           "added_columns": added, "removed_columns": removed, "numeric_drift_psi": drift,
           "note": "PSI >0.25 = investigate before loading; new columns need contract review."}
    json.dump(out, open("outputs/uc4_metrics.json", "w"), indent=2)
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
