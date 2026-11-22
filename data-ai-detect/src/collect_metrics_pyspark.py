"""Collect per-batch ETL metrics from raw_crs_ros_prfl using PySpark.

Computes the 9 features expected by Pipeline Watch:
1. From raw_crs_ros_prfl:
   - row_count, null_rate, duplicate_rate, distinct_keys_ratio, avg_amount
2. From job run audit (or pipeline CLI arguments):
   - day_of_week, reject_rate, runtime_min, late_minutes

Outputs:
  - data/today.csv   (daily single-batch run -> feed into src/score_daily.py)
  - data/history.csv (multi-batch historical backfill -> feed into src/train.py)

Usage:
  # Daily run from Airflow / Control-M:
  spark-submit src/collect_metrics_pyspark.py \
      --table raw.raw_crs_ros_prfl \
      --batch-id "raw_crs_ros_prfl_20261122" \
      --output data/today.csv \
      --runtime-min 25.0 \
      --late-minutes 0.0

  # History backfill across partitions for initial model training:
  spark-submit src/collect_metrics_pyspark.py \
      --table raw.raw_crs_ros_prfl \
      --backfill \
      --output data/history.csv
"""

import argparse
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

def parse_args():
    parser = argparse.ArgumentParser(description="Collect batch metrics from raw_crs_ros_prfl")
    parser.add_argument("--table", default="raw.raw_crs_ros_prfl", help="Target table name")
    parser.add_argument("--audit-table", default=None, help="Optional job run audit table")
    parser.add_argument("--batch-id", default=None, help="Batch ID string for daily single-batch runs")
    parser.add_argument("--batch-col", default="load_date", help="Date/partition/batch column in table")
    parser.add_argument("--output", default="data/today.csv", help="Output CSV path")
    parser.add_argument("--runtime-min", type=float, default=25.0, help="Job runtime in minutes")
    parser.add_argument("--late-minutes", type=float, default=0.0, help="Job delay past SLA in minutes")
    parser.add_argument("--reject-rate", type=float, default=0.0, help="Job reject rate (if known)")
    parser.add_argument("--numeric-col", default=None, help="Optional numeric column to track (e.g. risk_score)")
    parser.add_argument("--backfill", action="store_true", help="Group by batch_col across history instead of single batch")
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    spark = SparkSession.builder.appName("collector-raw-crs-ros-prfl").getOrCreate()
    df = spark.table(args.table)

    primary_key = ["profile_id"]
    customer_key = ["cust_id_num"]
    null_cols = ["profile_id", "cust_id_num"]

    null_expr = sum(F.col(c).isNull().cast("int") for c in null_cols) / float(len(null_cols))

    agg_exprs = [
        F.count("*").alias("row_count"),
        F.avg(null_expr).alias("null_rate"),
        (F.countDistinct(*customer_key) / F.count("*")).alias("distinct_keys_ratio"),
        (1.0 - (F.countDistinct(*primary_key) / F.count("*"))).alias("duplicate_rate")
    ]

    if args.numeric_col and args.numeric_col in df.columns:
        agg_exprs.append(F.avg(F.col(args.numeric_col)).alias("avg_amount"))
    else:
        agg_exprs.append(F.lit(0.0).alias("avg_amount"))

    if args.backfill:
        # Group across all historical batch dates for initial training (data/history.csv)
        data_metrics = (
            df.groupBy(args.batch_col)
              .agg(*agg_exprs)
              .withColumnRenamed(args.batch_col, "batch_id")
              .withColumn("day_of_week", (F.dayofweek(F.col("batch_id")) - 1) % 7)
              .withColumn("reject_rate", F.lit(args.reject_rate))
              .withColumn("runtime_min", F.lit(args.runtime_min))
              .withColumn("late_minutes", F.lit(args.late_minutes))
        )
    else:
        # Single daily batch execution (data/today.csv)
        batch_id_val = args.batch_id or "raw_crs_ros_prfl_batch"
        data_metrics = (
            df.agg(*agg_exprs)
              .withColumn("batch_id", F.lit(batch_id_val))
              .withColumn("day_of_week", (F.dayofweek(F.current_timestamp()) - 1) % 7)
              .withColumn("reject_rate", F.lit(args.reject_rate))
              .withColumn("runtime_min", F.lit(args.runtime_min))
              .withColumn("late_minutes", F.lit(args.late_minutes))
        )

    # If audit table is provided, join on batch_id
    if args.audit_table:
        runs = spark.table(args.audit_table)
        run_metrics = (
            runs.withColumn("runtime_min", (F.unix_timestamp("end_ts") - F.unix_timestamp("start_ts")) / 60.0)
                .withColumn("late_minutes", F.greatest((F.unix_timestamp("start_ts") - F.unix_timestamp("expected_start_ts")) / 60.0, F.lit(0.0)))
                .withColumn("reject_rate", F.when(F.col("input_count") > 0, F.col("reject_count") / F.col("input_count")).otherwise(0.0))
                .withColumn("day_of_week", (F.dayofweek("start_ts") - 1) % 7)
                .select("batch_id", "day_of_week", "reject_rate", "runtime_min", "late_minutes")
        )
        data_metrics = data_metrics.drop("day_of_week", "reject_rate", "runtime_min", "late_minutes")
        data_metrics = data_metrics.join(run_metrics, "batch_id", "inner")

    ordered_cols = [
        "batch_id", "day_of_week", "row_count", "null_rate",
        "duplicate_rate", "reject_rate", "avg_amount",
        "distinct_keys_ratio", "runtime_min", "late_minutes"
    ]
    final_metrics = data_metrics.select(*ordered_cols)

    # Write output CSV (coalesce to 1 to produce standard single CSV file)
    final_metrics.coalesce(1).write.mode("overwrite").option("header", True).csv(args.output)
    print(f"[collector] Successfully collected metrics -> {args.output}")

if __name__ == "__main__":
    main()
