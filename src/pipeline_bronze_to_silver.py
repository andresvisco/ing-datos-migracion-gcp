import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions, SetupOptions
import csv
import io
from datetime import datetime

# Cambia estos valores a los de tu proyecto/buckets/tabla
PROJECT_ID = "analitica-de-conversaciones"
BUCKET_INPUT = "gs://avlab-bronze-raw/raw/*.csv"
BQ_TABLE = "analitica-de-conversaciones.silver.avlab_silver_table_curated"
BQ_SCHEMA = "id:INTEGER,texto:STRING,fecha:TIMESTAMP"

def parse_csv(line):
    # Parsear una línea CSV y devolver un diccionario
    reader = csv.reader([line])
    for row in reader:
        if len(row) != 3:
            return None
        try:
            # Validación mínima
            return {
                'id': int(row[0]),
                'texto': row[1],
                'fecha': row[2]  # Suponiendo formato correcto YYYY-MM-DD HH:MM:SS
            }
        except Exception:
            return None

def run():
    # Opciones del pipeline
    options = PipelineOptions()
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = PROJECT_ID
    google_cloud_options.job_name = "bronze-to-silver-mvp"
    google_cloud_options.staging_location = f"gs://avlab-bronze-raw/staging"
    google_cloud_options.temp_location = f"gs://avlab-bronze-raw/temp"
    options.view_as(StandardOptions).runner = "DataflowRunner"
    options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=options) as p:
        (p
         | "Leer archivos CSV" >> beam.io.ReadFromText(BUCKET_INPUT, skip_header_lines=1)
         | "Parsear CSV" >> beam.Map(parse_csv)
         | "Filtrar nulos" >> beam.Filter(lambda x: x is not None)
         | "Escribir en BigQuery" >> beam.io.WriteToBigQuery(
                BQ_TABLE,
                schema=BQ_SCHEMA,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == "__main__":
    run()