# ETL Anomaly Detection

**Description:** Unsupervised detection of abnormal ETL batch runs using Isolation Forest — flags batches with unusual row counts, durations, and error rates without needing labelled failures. Built for DataStage / PySpark / Databricks-style pipelines.

## Experiment (synthetic)

- 2,000 batches, 100 planted anomalies
- Precision 0.82 · Recall 0.82 · ROC-AUC 0.994 · PR-AUC 0.935

## Run it

```bash
pip install -r requirements.txt
python src/generate_data.py
python src/detect.py
```

`ANALYSIS.md` compares models and lays out the production path. `demo/` is a small interactive app to score batches visually.
