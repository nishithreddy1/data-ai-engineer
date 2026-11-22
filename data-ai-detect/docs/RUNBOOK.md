# Pipeline Watch — Production Runbook

## Setup (once)
1. Collect 3–6 months of batch metrics (PySpark or Teradata collector from the real-data kit) → `data/history.csv`
2. `python src/train.py data/history.csv 0.03` → saves `models/pipeline_watch.pkl`
3. Sanity-check: open the flagged history batches — do they look like real bad days?

## Daily (scheduled after the load job)
```
collector (today's batch)  ->  data/today.csv
python src/score_daily.py data/today.csv     # exit 2 = anomalies found
python src/alert.py --send                   # Slack/email if flagged
```
- No alert → batch flows downstream automatically.
- Alert → check source file/job log, fix or rerun, note true/false alarm.

## Weekly
- Retrain on rolling last 3–6 months: `python src/train.py data/history.csv 0.03`
- Review false alarms: too many → lower contamination (0.02); missed bad batches → raise it (0.05).

## Tuning guide
| Symptom | Fix |
|---|---|
| Alert every month-end | Retrain (month-end becomes normal) or raise threshold via lower contamination |
| Real failure missed | Raise contamination to 0.05; check the metric actually moved |
| New source system added | Retrain with its history included |

## Files
- `docs/ARCHITECTURE_FLOW.md` — Visual architecture flow & step-by-step design
- `docs/architecture_flow.html` — Interactive browser-viewable visual diagrams
- `src/collect_metrics_pyspark.py` — Production PySpark metric collector (supports daily & `--backfill`)
- `src/collect_metrics_pyspark_template.py` — Minimal PySpark collector template
- `sql/collect_metrics_teradata.sql` — Teradata SQL metric collection query
- `src/train.py` — train + save model
- `src/score_daily.py` — score today, write alerts.txt, exit 2 if flagged
- `src/detect_real.py` — ad-hoc batch scoring tool
- `src/alert.py` — send alerts (dry-run default; `SLACK_WEBHOOK_URL` env var)
- `orchestration/airflow_dag.py` — Airflow DAG implementation
- `orchestration/CONTROL_M_GUIDE.md` — Control-M job flow & XML definition
- `models/pipeline_watch.pkl` — scaler + model + medians
