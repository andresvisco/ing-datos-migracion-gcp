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

# Ejemplo: Bucket de GCS
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

# Ejemplo: BigQuery Dataset
resource "google_bigquery_dataset" "bronze" {
  dataset_id                  = replace("${var.empresa}_${var.componente}_${var.dominio}_${var.entorno}", "-", "_")
  location                    = var.region
  labels                      = local.labels
  delete_contents_on_destroy  = true
}

# Ejemplo: Service Account
resource "google_service_account" "df" {
  account_id   = "sa-df-${var.dominio}-${var.entorno}"
  display_name = "Dataflow SA ${var.dominio}-${var.entorno}"
  description  = "Service account for Dataflow ${var.dominio} ${var.entorno}"
}