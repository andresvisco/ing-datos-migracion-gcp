import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions, SetupOptions
from datetime import datetime

# Configuración para entorno dev - Actualizado según nomenclatura MEDICUS
# Alineado con Documentacion/nomenclatura-gcp.md
PROJECT_ID = "medicus-data-dataml-dev"
BUCKET_INPUT = "gs://medicus-data-bronze-raw-dev-uscentral1/raw/*.parquet"  # Formato Parquet según estándar Bronze
BQ_TABLE = "medicus-data-dataml-dev.medicus_bronze_raw_acumulado.bronze_data_curated"
BQ_SCHEMA = "id:INTEGER,texto:STRING,fecha:TIMESTAMP"

def parse_parquet_record(record):
    """
    Procesa un registro de Parquet y lo transforma para BigQuery.
    Nota: ReadFromParquet devuelve diccionarios directamente con los datos parseados.
    Se aplica validación básica antes de escribir en BigQuery Silver.
    """
    try:
        # Validación mínima - ajustar según el esquema real de los datos
        if 'id' not in record or 'texto' not in record or 'fecha' not in record:
            return None
        
        return {
            'id': int(record['id']),
            'texto': str(record['texto']),
            'fecha': record['fecha']  # Parquet maneja timestamps nativamente
        }
    except Exception:
        return None

def run():
    # Opciones del pipeline para entorno dev
    # Job name alineado con nomenclatura: df-<pipeline>-<dominio>-<entorno>
    options = PipelineOptions()
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = PROJECT_ID
    google_cloud_options.job_name = "df-bronze-to-silver-data-dev"
    google_cloud_options.staging_location = f"gs://medicus-data-bronze-raw-dev-uscentral1/staging"
    google_cloud_options.temp_location = f"gs://medicus-data-bronze-raw-dev-uscentral1/temp"
    options.view_as(StandardOptions).runner = "DataflowRunner"
    options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=options) as p:
        (p
         # Lectura de archivos Parquet desde Bronze (no CSV)
         | "Leer archivos Parquet" >> beam.io.ReadFromParquet(BUCKET_INPUT)
         | "Parsear y validar registros" >> beam.Map(parse_parquet_record)
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