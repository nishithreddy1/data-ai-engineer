"""Airflow DAG for Pipeline Watch Anomaly Gate.

Pipeline:
  1. load_raw_crs_ros_prfl    -> Ingests raw data
  2. collect_metrics_pyspark  -> Computes the 9 quality metrics via PySpark -> data/today.csv
  3. score_batch_metrics      -> Evaluates Isolation Forest:
                                 - Exit code 0: Normal batch -> downstream ETL proceeds
                                 - Exit code 2: Anomaly found -> fails & triggers alert
  4. alert_on_anomaly         -> Sends Slack/email alert with plain-English diagnosis
  5. downstream_etl           -> Silver/Gold dimensional transformations
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["data-alerts@example.com"],
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="pipeline_watch_raw_crs_ros_prfl",
    default_args=default_args,
    description="ETL Batch Ingestion with Isolation Forest Anomaly Detection Gate",
    schedule_interval="0 4 * * *",  # Daily at 04:00 AM
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["pipeline-watch", "data-quality", "pyspark", "anomaly-detection"],
) as dag:

    # 1. Raw Ingestion Step
    load_raw_table = BashOperator(
        task_id="load_raw_crs_ros_prfl",
        bash_command="""
        echo "Running raw load for batch: {{ ds_nodash }}..."
        # your ingestion command / spark submit here
        """,
    )

    # 2. PySpark Metric Collection Step
    # Passes DAG run metadata (batch date, runtime) into collector
    collect_metrics = BashOperator(
        task_id="collect_metrics_pyspark",
        bash_command="""
        spark-submit \
            --master yarn \
            --deploy-mode client \
            src/collect_metrics_pyspark.py \
            --table raw.raw_crs_ros_prfl \
            --batch-id "raw_crs_ros_prfl_{{ ds_nodash }}" \
            --output "data/today.csv" \
            --runtime-min 25.0 \
            --late-minutes 0.0
        """,
    )

    # 3. Model Scoring Gate
    # Exits 0 on clean batch, exits 2 on anomaly detected
    score_today = BashOperator(
        task_id="score_batch_metrics",
        bash_command="python src/score_daily.py data/today.csv",
    )

    # 4. Anomaly Alerting Step (Slack / Webhook)
    # trigger_rule="all_failed" guarantees this executes ONLY when score_batch_metrics exits != 0
    alert_on_anomaly = BashOperator(
        task_id="alert_on_anomaly",
        bash_command="python src/alert.py --send",
        env={
            "SLACK_WEBHOOK_URL": "{{ var.value.SLACK_WEBHOOK_URL }}"
        },
        trigger_rule="all_failed",
    )

    # 5. Downstream Transformations (Only runs if score_batch_metrics exits 0)
    downstream_etl = EmptyOperator(
        task_id="downstream_transformations",
    )

    # Dependency graph
    load_raw_table >> collect_metrics >> score_today >> downstream_etl
    score_today >> alert_on_anomaly
