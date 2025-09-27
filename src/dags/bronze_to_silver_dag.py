from airflow import models
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.utils.dates import days_ago

PROJECT_ID = "analitica-de-conversaciones"
GCS_BUCKET = "avlab-bronze-raw"
GCS_PREFIX = "raw/"
DATAFLOW_PY_FILE = "gs://avlab-bronze-raw/code/pipeline_bronze_to_silver.py"
REGION = "us-central1"

default_args = {
    "start_date": days_ago(1),
}

with models.DAG(
    "bronze_to_silver_trigger",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['bronze', 'silver', 'dataflow'],
) as dag:

    wait_for_files = GCSObjectsWithPrefixExistenceSensor(
        task_id="wait_for_new_files",
        bucket=GCS_BUCKET,
        prefix=GCS_PREFIX,
        poke_interval=60,
        timeout=60 * 60,
        mode="poke"
    )

    run_dataflow = DataflowCreatePythonJobOperator(
        task_id="run_dataflow_bronze_to_silver",
        py_file=DATAFLOW_PY_FILE,
        location=REGION,
        project_id=PROJECT_ID,
        job_name="bronze-to-silver-{{ ds_nodash }}",
        # options={"input": f"gs://{GCS_BUCKET}/{GCS_PREFIX}*.csv"}
    )

    wait_for_files >> run_dataflow