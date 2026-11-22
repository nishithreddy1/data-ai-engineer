"""Pipeline Watch — ETL batch anomaly demo (Streamlit).

Run:  streamlit run app.py
Default data is the SYNTHETIC batch set from the ml-for-data-engineering
experiment (2,000 batches, 100 planted anomalies). Upload your own CSV
with the same metric columns to score real batch history; the
`is_anomaly` label column is optional and used only for evaluation.
"""
import io

import pandas as pd
import streamlit as st

from scoring import FEATURES, score_batches

st.set_page_config(page_title="Pipeline Watch", layout="wide")
st.title("Pipeline Watch — ETL batch anomaly detection")
st.caption(
    "Isolation Forest on per-batch metrics (row counts, null/duplicate/reject "
    "rates, runtime, lateness). Unsupervised: no labelled failures needed. "
    "Flagged batches go to a human review queue — nothing is auto-quarantined."
)

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Batch metrics CSV (optional)", type=["csv"])
    contamination = st.slider(
        "Flag rate (contamination)", min_value=0.01, max_value=0.10,
        value=0.05, step=0.01,
        help="Share of batches flagged for review. Tune to your alert budget.",
    )
    st.markdown(
        "**Required columns:** `" + "`, `".join(FEATURES) + "`\n\n"
        "Optional: `batch_id`, `is_anomaly` (evaluation only)."
    )

if uploaded is not None:
    df = pd.read_csv(uploaded)
    source = f"uploaded file: {uploaded.name}"
else:
    df = pd.read_csv("data/etl_batches.csv")
    source = "bundled SYNTHETIC demo data (2,000 batches, 100 planted anomalies)"

st.write(f"**Source:** {source} · **Rows:** {len(df):,}")

try:
    scored, metrics = score_batches(df, contamination=contamination)
except ValueError as e:
    st.error(str(e))
    st.stop()

flagged = scored[scored["flagged"] == 1]
st.subheader(f"Review queue — {len(flagged)} flagged batches (worst first)")

if metrics:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precision", metrics["precision"])
    c2.metric("Recall", metrics["recall"])
    c3.metric("ROC-AUC", metrics["roc_auc"])
    c4.metric("PR-AUC", metrics["pr_auc"])
    st.caption(
        "Labels present, so evaluation metrics are shown. On synthetic data "
        "with clear failure modes these are a proof of method, not a promise "
        "for real pipelines."
    )

st.dataframe(flagged, use_container_width=True)

st.subheader("Anomaly score distribution")
st.bar_chart(scored["anomaly_score"].sort_values(ascending=False).reset_index(drop=True))

st.subheader("Flagged vs normal — feature medians")
compare = pd.DataFrame({
    "flagged_median": flagged[FEATURES].median(),
    "normal_median": scored[scored["flagged"] == 0][FEATURES].median(),
})
st.dataframe(compare, use_container_width=True)

buf = io.StringIO()
scored.to_csv(buf, index=False)
st.download_button(
    "Download scored batches (CSV)",
    data=buf.getvalue(),
    file_name="scored_batches.csv",
    mime="text/csv",
)
