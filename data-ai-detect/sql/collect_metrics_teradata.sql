-- REAL per-batch ETL metrics in Teradata SQL.
-- Source 1: landed table (one row per record, batch_id + load_ts)
-- Source 2: job audit table (DataStage / Control-M run log)
-- Replace table/column names with yours. Output feeds detect_real.py.

WITH data_metrics AS (
    SELECT
        batch_id,
        COUNT(*)                                   AS row_count,
        AVG(CASE WHEN account_id IS NULL OR txn_id IS NULL
                  OR amount IS NULL OR txn_date IS NULL
                 THEN 1.0 ELSE 0.0 END)            AS null_rate,
        AVG(amount)                                AS avg_amount,
        CAST(COUNT(DISTINCT account_id, txn_id) AS FLOAT)
            / COUNT(*)                             AS distinct_keys_ratio
    FROM landed_transactions
    GROUP BY batch_id
),
run_metrics AS (
    SELECT
        batch_id,
        DAY_OF_WEEK(start_ts) - 1                  AS day_of_week,  -- Mon=0..Sun=6
        CASE WHEN input_count > 0
             THEN CAST(reject_count AS FLOAT) / input_count
             ELSE 0 END                            AS reject_rate,
        (end_ts - start_ts) MINUTE(4)              AS runtime_min,
        GREATEST((start_ts - expected_start_ts) MINUTE(4), 0)
                                                   AS late_minutes
    FROM etl_job_runs
)
SELECT
    d.batch_id,
    r.day_of_week,
    d.row_count,
    d.null_rate,
    1 - d.distinct_keys_ratio                      AS duplicate_rate,
    r.reject_rate,
    d.avg_amount,
    d.distinct_keys_ratio,
    r.runtime_min,
    r.late_minutes
FROM data_metrics d
JOIN run_metrics r ON d.batch_id = r.batch_id;
