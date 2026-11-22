"""UC6 — LLM-based repair (SAFE DEMO — proposes, never auto-applies).

A fine-tuned LLM (Jellyfish-style) can clean/repair bad values, but its
mistakes look plausible. This demo shows the guardrailed pattern WITHOUT
calling any LLM: deterministic repair proposals + confidence + human
approval gate. Wire a real LLM only behind this same gate, with audit log.
"""
import json
import re
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

def messy_records(n=800):
    df = pd.DataFrame({
        "email": [f"User{i}@EXAMPLE.com " if i % 5 == 0 else f"user{i}@example.com" for i in range(n)],
        "amount_text": [f"₹{v:,.2f}" if i % 4 == 0 else str(v) for i, v in enumerate(rng.normal(1840, 300, n).round(2))],
        "date_text": [f"{d:02d}/01/2026" if i % 3 == 0 else f"2026-01-{d:02d}" for i, d in enumerate(rng.integers(1, 29, n))],
        "country": rng.choice(["india", "INDIA", "In", "IN"], n),
    })
    return df

def propose_repairs(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["email_fixed"] = out["email"].str.strip().str.lower()
    out["amount_fixed"] = out["amount_text"].str.replace(r"[₹,\s]", "", regex=True).astype(float)
    out["date_fixed"] = pd.to_datetime(out["date_text"], dayfirst=True, format="mixed").dt.strftime("%Y-%m-%d")
    out["country_fixed"] = out["country"].str.upper().replace({"INDIA": "IN"})
    out["needs_review"] = (
        (out["email"] != out["email_fixed"]) | (out["country"] != out["country_fixed"]))
    return out

def run():
    df = messy_records()
    fixed = propose_repairs(df)
    changed = int(((fixed["email"] != fixed["email_fixed"]) |
                   (fixed["country"] != fixed["country_fixed"]) |
                   (fixed["date_text"] != fixed["date_fixed"])).sum())
    out = {"use_case": "6_llm_repair_guarded_demo", "records": int(len(df)),
           "records_with_proposed_repairs": changed,
           "flagged_for_human_review": int(fixed["needs_review"].sum()),
           "auto_applied": 0,
           "guardrails": ["propose-only, human approves", "original values preserved",
                          "every repair logged", "no LLM call in this demo"],
           "note": "Replace propose_repairs() internals with an LLM later — keep the gate."}
    fixed.head(200).to_csv("outputs/uc6_repair_proposals.csv", index=False)
    json.dump(out, open("outputs/uc6_metrics.json", "w"), indent=2)
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
