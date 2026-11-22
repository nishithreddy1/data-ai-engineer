# Data AI Engineer

Data engineering + machine learning projects by a Data + AI Engineer (DataStage/CDC, Teradata → Spark Delta migration, PySpark, Databricks, GCP BigQuery, Airflow/Control-M, RAG POCs).

## Projects in this repo

### ML in Data Engineering — `ml-in-data-engineering/`
Six runnable ML use cases for data pipelines, verified on synthetic data:
1. Batch anomaly detection (Isolation Forest, P/R 0.82, AUC 0.994)
2. Bad-record classification & DQ scoring
3. Pipeline failure & SLA prediction
4. Schema drift & semantic typing (PSI)
5. Sequence anomaly detection (autoencoder)
6. Guarded LLM-based repair (proposals only, 0 auto-applied)

### ETL Anomaly Detection — `etl-anomaly-detection/`
Unsupervised ETL batch anomaly detection with Isolation Forest (2,000 synthetic batches, 100 planted anomalies, AUC 0.994), plus a small demo app in `demo/`.

## Notes

- All ML experiments use synthetic data; scores are a starting point
