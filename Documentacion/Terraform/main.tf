terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.9.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

locals {
  sanitized_project = replace(lower(var.project_id), "_", "-")
  bucket_prefix     = replace(lower("${var.project_id}-${var.environment}"), "_", "-")

  resource_labels = merge(
    {
      environment = var.environment
      managed_by  = "terraform"
      project     = var.project_id
    },
    var.additional_labels
  )

  bigquery_datasets = [
    {
      id          = "bronze"
      description = "Raw landing zone for ingested data"
    },
    {
      id          = "silver"
      description = "Curated analytics-ready layer"
    }
  ]

  dataflow_roles = [
    "roles/dataflow.worker",
    "roles/storage.objectAdmin",
    "roles/bigquery.dataEditor",
    "roles/spanner.databaseUser"
  ]

  required_services = [
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "spanner.googleapis.com",
    "dataflow.googleapis.com",
    "compute.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com"
  ]
}

variable "project_id" {
  description = "ID del proyecto GCP donde se desplegará la plataforma de datos"
  type        = string
}

variable "region" {
  description = "Región por defecto para los recursos regionales"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zona por defecto para recursos zonales"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Etiqueta de entorno (dev, qa, prod, etc.)"
  type        = string
  default     = "dev"
}

variable "dataset_location" {
  description = "Localización de los datasets de BigQuery"
  type        = string
  default     = "US"
}

variable "spanner_config" {
  description = "Configuración regional de Spanner (ver documentación de Google)"
  type        = string
  default     = "regional-us-central1"
}

variable "spanner_processing_units" {
  description = "Processing units asignados a la instancia de Spanner"
  type        = number
  default     = 100
}

variable "subnet_cidr" {
  description = "CIDR para la subred principal del data platform"
  type        = string
  default     = "10.20.0.0/24"
}

variable "additional_labels" {
  description = "Etiquetas adicionales a aplicar a los recursos"
  type        = map(string)
  default     = {}
}

variable "dataflow_template_gcs_path" {
  description = "Ruta opcional al template de Dataflow (gs://bucket/templates/template.json)"
  type        = string
  default     = ""
}

variable "deploy_example_dataflow_job" {
  description = "Si es true, intentará desplegar un job de Dataflow con el template proporcionado"
  type        = bool
  default     = false
}

resource "google_project_service" "required" {
  for_each = toset(locals.required_services)

  service            = each.key
  disable_on_destroy = false
}

resource "google_compute_network" "data_platform" {
  name                    = "${local.sanitized_project}-${var.environment}-net"
  auto_create_subnetworks = false
  routing_mode            = "GLOBAL"
  description             = "Red VPC dedicada a la plataforma de datos"
}

resource "google_compute_subnetwork" "data_platform" {
  name          = "${local.sanitized_project}-${var.environment}-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.data_platform.id
  description   = "Subred principal para cargas de Dataflow y servicios gestionados"

  secondary_ip_range {
    range_name    = "dataflow-workers"
    ip_cidr_range = cidrsubnet(var.subnet_cidr, 4, 1)
  }
}

resource "google_storage_bucket" "raw" {
  name                        = "${local.bucket_prefix}-raw"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
  labels                      = locals.resource_labels

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "staging" {
  name                        = "${local.bucket_prefix}-staging"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
  labels                      = locals.resource_labels
}

resource "google_storage_bucket" "dataflow_temp" {
  name                        = "${local.bucket_prefix}-dataflow-temp"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
  labels                      = locals.resource_labels

  versioning {
    enabled = true
  }
}

resource "google_bigquery_dataset" "layers" {
  for_each = { for dataset in locals.bigquery_datasets : dataset.id => dataset }

  dataset_id    = each.value.id
  friendly_name = upper(each.value.id)
  description   = each.value.description
  location      = var.dataset_location
  labels        = locals.resource_labels
}

resource "google_spanner_instance" "core" {
  name             = "${local.sanitized_project}-${var.environment}-spanner"
  display_name     = "${upper(var.environment)} Data Platform"
  config           = var.spanner_config
  processing_units = var.spanner_processing_units
  labels           = locals.resource_labels
}

resource "google_spanner_database" "core" {
  instance = google_spanner_instance.core.name
  name     = "platform-core"

  ddl = [
    "CREATE TABLE metadata (id STRING(36) NOT NULL, created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true)) PRIMARY KEY (id)",
  ]
}

resource "google_service_account" "dataflow" {
  account_id   = "dataflow-${var.environment}"
  display_name = "Dataflow ${upper(var.environment)} Service Account"
}

resource "google_project_iam_member" "dataflow_roles" {
  for_each = toset(locals.dataflow_roles)

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.dataflow.email}"
}

resource "google_storage_bucket_iam_member" "dataflow_staging" {
  bucket = google_storage_bucket.dataflow_temp.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.dataflow.email}"
}

resource "google_bigquery_dataset_iam_member" "dataflow_rw" {
  for_each = google_bigquery_dataset.layers

  dataset_id = each.value.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dataflow.email}"
}

resource "google_dataflow_job" "example" {
  count = var.deploy_example_dataflow_job && length(var.dataflow_template_gcs_path) > 0 ? 1 : 0

  name                  = "${local.sanitized_project}-${var.environment}-example-job"
  template_gcs_path     = var.dataflow_template_gcs_path
  temp_gcs_location     = google_storage_bucket.dataflow_temp.url
  service_account_email = google_service_account.dataflow.email
  region                = var.region
  parameters = {
    environment = var.environment
  }
  depends_on = [
    google_project_service.required,
    google_storage_bucket.dataflow_temp,
    google_service_account.dataflow,
    google_compute_subnetwork.data_platform
  ]
}

output "gcs_buckets" {
  description = "Buckets principales del data lake"
  value = {
    raw     = google_storage_bucket.raw.name
    staging = google_storage_bucket.staging.name
    temp    = google_storage_bucket.dataflow_temp.name
  }
}

output "bigquery_datasets" {
  description = "Datasets de BigQuery creados"
  value = { for k, dataset in google_bigquery_dataset.layers : k => dataset.dataset_id }
}

output "spanner_connection" {
  description = "Cadena de conexión a la base de datos de Spanner"
  value       = "projects/${var.project_id}/instances/${google_spanner_instance.core.name}/databases/${google_spanner_database.core.name}"
}

output "dataflow_service_account_email" {
  description = "Service account utilizado por Dataflow"
  value       = google_service_account.dataflow.email
}
