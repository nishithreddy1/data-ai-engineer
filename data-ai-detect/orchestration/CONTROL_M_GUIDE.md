# Control-M Job Flow Specification: Pipeline Watch Anomaly Gate

This document specifies the exact Control-M SMART Folder and Job definitions to gate ETL loads on `raw_crs_ros_prfl`.

---

## 1. Flow Diagram

```text
[LOAD_RAW_CRS_ROS_PRFL]
         |
         v
[COLLECT_PYSPARK_METRICS]
         |
         v
[SCORE_DAILY_METRICS]
      /         \
 (RC = 0)     (RC = 2)
    /             \
   v               v
[DOWNSTREAM_ETL]  [ALERT_SLACK_NOTIFY]
 (DO OK)           (DO NOTOK / SHOUT)
```

---

## 2. Job Definitions

### Job 1: `LOAD_RAW_CRS_PRFL`
* **Application:** DATA_PLATFORM
* **Sub-Application:** INGESTION
* **Job Type:** Command
* **Command:** `/opt/scripts/ingest_crs_ros_prfl.sh %%$ODATE`
* **OUT Conditions:** `LOAD_RAW_CRS_PRFL-TO-COLLECT_METRICS`

---

### Job 2: `COLLECT_PYSPARK_METRICS`
* **Application:** DATA_PLATFORM
* **Sub-Application:** QUALITY_GATE
* **Job Type:** Command
* **IN Conditions:** `LOAD_RAW_CRS_PRFL-TO-COLLECT_METRICS`
* **Command:**
  ```bash
  spark-submit \
    --master yarn \
    /opt/pipeline-watch/src/collect_metrics_pyspark.py \
    --table raw.raw_crs_ros_prfl \
    --batch-id "raw_crs_ros_prfl_%%$ODATE" \
    --output "/opt/pipeline-watch/data/today.csv" \
    --runtime-min %%ELAPTIME \
    --late-minutes 0.0
  ```
* **OUT Conditions:** `COLLECT_METRICS-TO-SCORE_METRICS`

---

### Job 3: `SCORE_DAILY_METRICS` (The Quality Gate)
* **Application:** DATA_PLATFORM
* **Sub-Application:** QUALITY_GATE
* **Job Type:** Command
* **IN Conditions:** `COLLECT_METRICS-TO-SCORE_METRICS`
* **Command:**
  ```bash
  python /opt/pipeline-watch/src/score_daily.py /opt/pipeline-watch/data/today.csv
  ```
* **ON / DO Actions (Crucial Branching Logic):**
  | Condition (ON) | Return Code (CODE) | Action (DO) | Description |
  | :--- | :--- | :--- | :--- |
  | `ON STATEMENT *` | `CODE = 0` | `DO OK` <br> `DO ADD COND (SCORE_METRICS_OK)` | Batch is normal. Allows downstream jobs to trigger. |
  | `ON STATEMENT *` | `CODE = 2` | `DO NOTOK` <br> `DO ADD COND (SCORE_METRICS_ANOMALY)` <br> `DO SHOUT "Pipeline Watch: Anomaly detected on raw_crs_ros_prfl batch %%$ODATE"` | Anomaly detected! Halts downstream flow and triggers alert. |
  | `ON STATEMENT *` | `CODE = 1` | `DO NOTOK` <br> `DO SHOUT "Pipeline Watch: Script crashed with execution error"` | Python environment or syntax crash. |

---

### Job 4: `ALERT_SLACK_NOTIFY`
* **Application:** DATA_PLATFORM
* **Sub-Application:** QUALITY_GATE
* **Job Type:** Command
* **IN Conditions:** `SCORE_METRICS_ANOMALY`
* **Command:**
  ```bash
  export SLACK_WEBHOOK_URL="%%SLACK_WEBHOOK"
  python /opt/pipeline-watch/src/alert.py --send
  ```
* **ON / DO Actions:**
  * `ON STATEMENT * CODE = 0`: `DO OK`

---

### Job 5: `DOWNSTREAM_TRANSFORMS`
* **Application:** DATA_PLATFORM
* **Sub-Application:** TRANSFORMATIONS
* **Job Type:** Command
* **IN Conditions:** `SCORE_METRICS_OK`
* **Command:** `/opt/scripts/run_silver_gold_models.sh`

---

## 3. Control-M XML Definition Snippet

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FOLDER FOLDER_NAME="SMART_PIPELINE_WATCH_RAW_CRS" REAL_FOLDER_ID="0" TYPE="1">
    <JOB JOBNAME="SCORE_DAILY_METRICS" APPLICATION="DATA_PLATFORM" SUB_APPLICATION="QUALITY_GATE" CMDLINE="python /opt/pipeline-watch/src/score_daily.py /opt/pipeline-watch/data/today.csv">
        <INCOND COND="COLLECT_METRICS-TO-SCORE_METRICS" AND_OR="A"/>
        
        <!-- Clean batch: exit code 0 -->
        <ON STMT="*" CODE="0">
            <DOMAIL/>
            <DOCOND COND="SCORE_METRICS_OK" SIGN="+"/>
            <DOACTION ACTION="OK"/>
        </ON>

        <!-- Anomaly detected: exit code 2 -->
        <ON STMT="*" CODE="2">
            <DOCOND COND="SCORE_METRICS_ANOMALY" SIGN="+"/>
            <DOSHOUT MESSAGE="Pipeline Watch: Anomaly detected on raw_crs_ros_prfl" URGENCY="R"/>
            <DOACTION ACTION="NOTOK"/>
        </ON>

        <!-- Failure: exit code 1 -->
        <ON STMT="*" CODE="1">
            <DOSHOUT MESSAGE="Pipeline Watch: Script execution failure" URGENCY="R"/>
            <DOACTION ACTION="NOTOK"/>
        </ON>
    </JOB>
</FOLDER>
```
