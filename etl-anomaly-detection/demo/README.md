# Pipeline Watch — ETL batch anomaly demo

Built 2026-11-22. Local demo only — nothing deployed, published, or spent.

## What it is

A Streamlit UI over the verified Isolation Forest experiment from
`ml-for-data-engineering/` (same method, same synthetic data). It turns the
research + code + 11-page report delivered 2026-11-22 into something
clickable:

- **Review queue:** flagged batches, worst first, with anomaly scores.
- **Flag-rate slider (1–10%):** tune to an alert budget; rescored live.
- **Evaluation metrics** (precision/recall/ROC-AUC/PR-AUC) shown only when
  the input carries an `is_anomaly` label — labels are never used to train.
- **Flagged vs normal feature medians** — why a batch looks odd.
- **Upload your own CSV** with the same metric columns to score real batch
  history (DataStage job logs / Teradata load stats / PySpark job metrics).
- **Download** the scored CSV.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

## Verified (2026-11-22, sandbox)

- `scoring.score_batches` on the bundled data reproduces the experiment's
  `outputs/metrics.json` exactly: precision 0.82, recall 0.82,
  ROC-AUC 0.994, PR-AUC 0.935 (2,000 batches, 100 planted anomalies).
- No-label path (real-world case) scores and flags without metrics.
- Missing-column input raises a clear error.
- Streamlit `AppTest` runs the full UI with no exceptions; metrics,
  tables, chart, and download button render.

## Honest limits

- Bundled data is **synthetic** with clear failure modes (volume drop,
  null spike, duplicate surge, late arrival, runtime blowout). Real
  pipelines are noisier — treat the numbers as proof of method.
- No auth, no persistence, no alerting (email/Teams), no retraining
  schedule. Those are production steps, deliberately out of this demo.
- Not yet run in a real browser by the author; AppTest covers script
  execution and rendering, not visual layout.

## How this relates to the DataPilot plan (2026-11-20)

The DataPilot MVP scoped ingest → profile → clean → EDA → model compare →
export (~2 weeks, Option A FastAPI + Streamlit). Pipeline Watch is a
narrower first slice of that shape — ingest → score → review → export —
built on code that already exists and is verified, matched to your actual
DataStage/Teradata/PySpark batch work. It can stand alone as the first
"Built" demo, or become DataPilot's anomaly module later.

## Optional website entry (only if you approve the wording)

- status: `Built · Local demo (synthetic data)`
- tags: `Python, scikit-learn, Streamlit, Isolation Forest`
- brief: "Unsupervised anomaly detection on ETL batch metrics. Isolation
  Forest scores each batch (row counts, null/duplicate/reject rates,
  runtime, lateness); flagged batches go to a human review queue. On
  2,000 synthetic batches with 100 planted failures: precision/recall
  0.82, ROC-AUC 0.994. Demo runs locally; production steps (real job-log
  feeds, alerting, scheduled retraining) not yet built."

Nothing here changes the website until you say so.
