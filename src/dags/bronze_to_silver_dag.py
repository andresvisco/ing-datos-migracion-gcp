from airflow import models
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.utils.dates import days_ago

# Configuración para entorno dev - Actualizado según nomenclatura MEDICUS
# Alineado con Documentacion/nomenclatura-gcp.md
PROJECT_ID = "medicus-data-dataml-dev"
GCS_BUCKET = "medicus-data-bronze-raw-dev-uscentral1"
GCS_PREFIX = "raw/"  # Archivos Parquet en formato Bronze
DATAFLOW_PY_FILE = f"gs://{GCS_BUCKET}/code/pipeline_bronze_to_silver.py"
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
    tags=['bronze', 'silver', 'dataflow', 'dev'],  # Tag 'dev' añadido para identificar entorno
) as dag:

    # Sensor que espera archivos Parquet nuevos en Bronze
    wait_for_files = GCSObjectsWithPrefixExistenceSensor(
        task_id="wait_for_new_files",
        bucket=GCS_BUCKET,
        prefix=GCS_PREFIX,
        poke_interval=60,
        timeout=60 * 60,
        mode="poke"
    )

    # Job name alineado con nomenclatura: df-<pipeline>-<dominio>-<entorno>
    run_dataflow = DataflowCreatePythonJobOperator(
        task_id="run_dataflow_bronze_to_silver",
        py_file=DATAFLOW_PY_FILE,
        location=REGION,
        project_id=PROJECT_ID,
        job_name="df-bronze-to-silver-data-dev-{{ ds_nodash }}",
        # Archivos Parquet en formato Bronze
        # options={"input": f"gs://{GCS_BUCKET}/{GCS_PREFIX}*.parquet"}
    )

    wait_for_files >> run_dataflow