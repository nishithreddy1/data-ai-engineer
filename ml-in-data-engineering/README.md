# ML in Data Engineering

**Description:** Six machine-learning use cases that plug into data pipelines — anomaly detection, data-quality scoring, SLA risk prediction, schema-drift monitoring, sequence detection, and guarded LLM repair — each as a runnable Python module with verified results on synthetic data.

| # | Use case | Model | Verified result (synthetic) |
|---|----------|-------|------------------------------|
| 1 | Batch anomaly detection | Isolation Forest | Precision/recall 0.82, ROC-AUC 0.994 |
| 2 | Bad-record classification & DQ scoring | Gradient boosting | F1 1.0 (synthetic data too clean — flagged) |
| 3 | Pipeline failure & SLA prediction | Gradient boosting | AUC 0.669; tune threshold to alert budget |
| 4 | Schema drift & semantic typing | PSI + rule typing | PSI 2.665 = major drift detected |
| 5 | Sequence anomaly detection | Autoencoder | Recall 0.957 / precision 0.265 |
| 6 | LLM-based repair (guarded) | Proposal-only demo | 735 proposals, 0 auto-applied |

## Run it

```bash
pip install -r requirements.txt
python src/uc1_batch_anomaly.py
```

Each module writes metrics to `outputs/`. All data is synthetic — a starting point, not production proof.
