# Módulo de nomenclatura MEDICUS para recursos GCP
# Alineado con Documentacion/nomenclatura-gcp.md
#
# Configuración de ejemplo para entorno dev:
#   empresa = "medicus"
#   plataforma = "data"
#   dominio = "bronze" (o según el dominio específico)
#   componente = "raw"
#   entorno = "dev"
#   region = "uscentral1"
#
# Resultado ejemplo: medicus-data-bronze-raw-dev-uscentral1
# Para el proyecto dev actual se usa: medicus-data-dataml-dev

variable "empresa" { type = string }
variable "plataforma" { type = string }
variable "dominio" { type = string }
variable "componente" { type = string }
variable "entorno" { type = string }
variable "region" { type = string }
variable "sufijo_opcional" { type = string; default = "" }

locals {
  # Estructura base nomenclatura
  resource_name = join("-", compact([
    var.empresa,
    var.plataforma,
    var.dominio,
    var.componente,
    var.entorno,
    var.region,
    var.sufijo_opcional != "" ? var.sufijo_opcional : null
  ]))

  labels = {
    project        = "ing-datos-migracion-gcp"
    business_unit  = "medicus-data"
    environment    = var.entorno
    domain         = var.dominio
    managed_by     = "terraform"
    owner          = "data-platform"
  }
}

# Ejemplo: Bucket de GCS para capa Bronze
# Configuración dev: medicus-data-bronze-raw-dev-uscentral1
# Los archivos en Bronze se almacenan en formato Parquet (no CSV)
resource "google_storage_bucket" "raw" {
  name     = "${local.resource_name}"
  location = var.region
  labels   = local.labels

  uniform_bucket_level_access = true
  force_destroy = false

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 180 }
  }
}

# Ejemplo: BigQuery Dataset para capa Bronze
# Configuración dev: medicus_bronze_raw_acumulado en medicus-data-dataml-dev
resource "google_bigquery_dataset" "bronze" {
  dataset_id                  = replace("${var.empresa}_${var.componente}_${var.dominio}_${var.entorno}", "-", "_")
  location                    = var.region
  labels                      = local.labels
  delete_contents_on_destroy  = true
}

# Ejemplo: Service Account para Dataflow
# Configuración dev: sa-df-data-dev para pipelines Bronze→Silver
resource "google_service_account" "df" {
  account_id   = "sa-df-${var.dominio}-${var.entorno}"
  display_name = "Dataflow SA ${var.dominio}-${var.entorno}"
  description  = "Service account for Dataflow ${var.dominio} ${var.entorno}"
}