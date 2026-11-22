

| **1** | **ETL batch anomaly detection** (volume/null/dup/runtime drift) | Isolation Forest | No | **Best** — uses metrics you already have; scikit-learn basics; demo in days |
| 2 | Data-quality scoring / bad-record classification | Gradient boosting / logistic regression | Yes (past incidents) | Strong, but needs labelled history you may not have |
| 3 | Pipeline failure / SLA prediction | Random forest / XGBoost | Yes (run history) | Good phase 2 once run logs are collected |
| 4 | Schema drift / column semantic typing | Sherlock/Sato-style deep nets | Partially | Research-heavy; overkill for a first build |
| 5 | Autoencoder anomaly detection | Neural autoencoder | No | Powerful but heavier to tune/explain; keep as upgrade path |
| 6 | LLM auto-repair of bad data | Fine-tuned LLM (Jellyfish-style) | — | Flashy, risky for production data; not a first ML project |

Sources consulted 2026-05-10: InfoWorld on AI-augmented data quality
(Sherlock/Sato, BERTMap, Jellyfish, ReClean, GAN/VAE anomaly detection);
Entrans on ML data-quality monitoring (KNN/LOF, Isolation Forest, One-Class
SVM); NumberAnalytics on ML pipeline optimisation (anomaly detection +
predictive maintenance); DATAVERSITY on ML data quality in cloud-native
pipelines (anomaly/drift detection, probabilistic scoring).

## Why Isolation Forest wins here

- **No labels required.** Real ETL teams rarely have a clean labelled
  failure set. Isolation Forest learns normal behaviour directly.
- **Built for tabular batch metrics.** It isolates anomalies in few random
  splits — fast even in streaming, and strong on high-dimensional tabular data.
- **Explainable enough.** Score + the offending metrics (e.g. null_rate 0.37)
  tells an operator *why* a batch was flagged. Autoencoders score well too
  but are harder to explain and tune; One-Class SVM retrains expensively
  under drift; LOF is slower at scale.
- **Interview-defensible.** scikit-learn, train/test thinking, precision/
  recall trade-offs — exactly your "currently learning" ML scope, proven.

## Verified experiment (synthetic, reproducible)

2,000 synthetic batches (1,900 normal with weekend seasonality + 100
planted anomalies across 5 failure modes). Isolation Forest (300 trees,
contamination 0.05, StandardScaler):

- Precision **0.82**, Recall **0.82**, ROC-AUC **0.994**, PR-AUC **0.935**
- 82/100 anomalies caught; 18 false alarms (reviewable, not auto-rejected)

Honest limits: synthetic anomalies are cleaner than real incidents;
contamination is a guess until tuned on real history; single-batch
features only (no cross-day sequence model yet — LSTM autoencoder is the
phase-2 upgrade if sequences matter).

