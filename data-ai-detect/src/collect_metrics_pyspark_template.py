"""Collect REAL per-batch ETL metrics with PySpark (Databricks / Spark Delta).

Computes the same 9 features the anomaly model uses, from two real sources:

1. LANDED TABLE (one row per source record, with batch_id + load_ts)
   -> row_count, null_rate, duplicate_rate, avg_amount, distinct_keys_ratio
2. JOB RUN TABLE (one row per batch run: batch_id, start_ts, end_ts,
   expected_start_ts, reject_count, input_count)
   -> runtime_min, late_minutes, reject_rate, day_of_week

Replace the table/column names below with yours. Output: one row per batch,
written as CSV/Delta for detect_real.py. No labels needed.
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# --- EDIT THESE to your tables/columns ---
LANDED_TABLE = "catalog.schema.landed_transactions"   # Delta / Hive table
JOB_RUN_TABLE = "catalog.schema.etl_job_runs"         # from Airflow/Control-M/DataStage audit
KEY_COLS = ["account_id", "txn_id"]                   # business key for duplicates
AMOUNT_COL = "amount"
NULL_CHECK_COLS = ["account_id", "txn_id", "amount", "txn_date"]  # columns that must not be null
OUTPUT_PATH = "dbfs:/tmp/etl_batch_metrics"           # or a Delta table name
# ------------------------------------------

spark = SparkSession.builder.appName("etl-batch-metrics").getOrCreate()

landed = spark.table(LANDED_TABLE)
runs = spark.table(JOB_RUN_TABLE)

# 1) Per-batch data metrics from the landed table
null_expr = sum(F.col(c).isNull().cast("int") for c in NULL_CHECK_COLS) / len(NULL_CHECK_COLS)
data_metrics = (
    landed.groupBy("batch_id")
    .agg(
        F.count("*").alias("row_count"),
        F.avg(null_expr).alias("null_rate"),
        F.avg(F.col(AMOUNT_COL)).alias("avg_amount"),
        (F.countDistinct(*KEY_COLS) / F.count("*")).alias("distinct_keys_ratio"),
    )
    .withColumn("duplicate_rate", 1 - F.col("distinct_keys_ratio"))
)

# 2) Per-batch run metrics from the job audit table
run_metrics = (
    runs.withColumn("runtime_min",
                    (F.unix_timestamp("end_ts") - F.unix_timestamp("start_ts")) / 60)
        .withColumn("late_minutes",
                    F.greatest((F.unix_timestamp("start_ts")
                                - F.unix_timestamp("expected_start_ts")) / 60, F.lit(0)))
        .withColumn("reject_rate",
                    F.when(F.col("input_count") > 0,
                           F.col("reject_count") / F.col("input_count")).otherwise(0))
        .withColumn("day_of_week", F.dayofweek("start_ts") - 1)  # Mon=0 .. Sun=6 approx
        .select("batch_id", "day_of_week", "reject_rate", "runtime_min", "late_minutes")
)

metrics = data_metrics.join(run_metrics, "batch_id", "inner")

metrics.write.mode("overwrite").option("header", True).csv(OUTPUT_PATH)
print(f"Wrote {metrics.count()} batch rows to {OUTPUT_PATH}")
