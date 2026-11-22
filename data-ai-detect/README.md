# Data-AI-Detect — Production Batch Anomaly Detection

**Description:** Production ETL batch anomaly detection: train Isolation Forest on batch-metric history, score every new batch daily, alert with plain-English reasons. No labels needed.

## Architecture & Workflow
See [docs/ARCHITECTURE_FLOW.md](docs/ARCHITECTURE_FLOW.md) for the visual architecture diagram, metric mapping, exit codes, and operational phases.

## Repository Structure

- `src/collect_metrics_pyspark.py`: Production PySpark collector (supports single batch & `--backfill`).
- `src/collect_metrics_pyspark_template.py`: Minimal PySpark reference collector.
- `sql/collect_metrics_teradata.sql`: Teradata SQL collector query.
- `src/train.py`: Train Isolation Forest on batch history (`models/pipeline_watch.pkl`).
- `src/score_daily.py`: Daily batch scoring gate (Exit code 0 = normal, 2 = anomalies).
- `src/detect_real.py`: Exploratory/ad-hoc batch scoring without model persistence.
- `src/alert.py`: Slack/email alert dispatcher with plain-English reasons.
- `orchestration/`: Airflow DAG (`airflow_dag.py`) and Control-M flow (`CONTROL_M_GUIDE.md`).
- `docs/`: Visual interactive diagrams (`architecture_flow.html`), markdown architecture (`ARCHITECTURE_FLOW.md`), and runbook (`RUNBOOK.md`).

## Quick start

```bash
pip install -r requirements.txt

# 1. Collect metrics (PySpark collector for raw_crs_ros_prfl)
spark-submit src/collect_metrics_pyspark.py --backfill --output data/history.csv

# 2. Train model (once, then weekly retrain)
python src/train.py data/history.csv 0.03

# 3. Daily scoring (exit 2 = anomalies found)
python src/score_daily.py data/today.csv

# 4. Alert (dry-run; --send for Slack)
python src/alert.py
```

## Schedulers & Orchestration
Full workflow DAGs and job configurations are provided in `orchestration/`:
- `orchestration/airflow_dag.py`: Production Airflow DAG with quality gate branching.
- `orchestration/CONTROL_M_GUIDE.md`: Control-M ON/DO condition definitions for Return Code 2 branching.

See `docs/RUNBOOK.md` for the full daily/weekly operating guide and tuning table.
