import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions, SetupOptions
from datetime import datetime

# Configuración del entorno dev según nomenclatura-gcp.md
# PROJECT_ID: medicus-data-dataml-dev alineado con convención medicus-data-<entorno>
PROJECT_ID = "medicus-data-dataml-dev"
# BUCKET_INPUT: Archivos en formato Parquet desde Bronze Raw Landing Zone
# Convención: medicus-data-bronze-raw-dev-uscentral1
BUCKET_INPUT = "gs://medicus-data-bronze-raw-dev-uscentral1/raw/*.parquet"
# BQ_TABLE: Dataset Silver según nomenclatura medicus_<layer>_<dominio>_<entorno>
BQ_TABLE = "medicus-data-dataml-dev.medicus_silver_curated.table_curated"
BQ_SCHEMA = "id:INTEGER,texto:STRING,fecha:TIMESTAMP"

def parse_parquet_record(record):
    """
    Procesa un registro de Parquet y devuelve un diccionario.
    Los archivos Parquet ya vienen estructurados, por lo que no necesitamos parsear CSV.
    Aplicamos validación mínima para asegurar integridad de datos.
    """
    try:
        # Validación mínima: verificar campos requeridos
        if not all(k in record for k in ['id', 'texto', 'fecha']):
            return None
        return {
            'id': int(record['id']),
            'texto': str(record['texto']),
            'fecha': record['fecha']  # Formato TIMESTAMP ya viene estructurado en Parquet
        }
    except Exception:
        return None

def run():
    # Opciones del pipeline - configuración para entorno dev
    options = PipelineOptions()
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = PROJECT_ID
    # Job name siguiendo convención: df-<pipeline>-<dominio>-<entorno>
    google_cloud_options.job_name = "df-bronze-to-silver-dev"
    # Staging y temp locations usando bucket bronze
    google_cloud_options.staging_location = f"gs://medicus-data-bronze-raw-dev-uscentral1/staging"
    google_cloud_options.temp_location = f"gs://medicus-data-bronze-raw-dev-uscentral1/temp"
    options.view_as(StandardOptions).runner = "DataflowRunner"
    options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=options) as p:
        (p
         # Leer archivos Parquet desde Bronze Raw Landing Zone
         | "Leer archivos Parquet" >> beam.io.ReadFromParquet(BUCKET_INPUT)
         | "Parsear y validar" >> beam.Map(parse_parquet_record)
         | "Filtrar nulos" >> beam.Filter(lambda x: x is not None)
         | "Escribir en BigQuery Silver" >> beam.io.WriteToBigQuery(
                BQ_TABLE,
                schema=BQ_SCHEMA,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == "__main__":
    run()