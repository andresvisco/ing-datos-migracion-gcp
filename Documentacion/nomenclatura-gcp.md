# Guía de nomenclatura para la plataforma de datos de MEDICUS en GCP

> Proyecto: `ing-datos-migracion-gcp`

Esta guía define las convenciones de nombres y etiquetas para los recursos de Google Cloud Platform utilizados en la migración del área de datos de MEDICUS. El objetivo es facilitar la trazabilidad, operación y gobernanza multientorno (dev, qa, prod) y multidominio.

## Principios generales

- **Estructura base**: `<empresa>-<plataforma>-<dominio>-<componente>-<entorno>-<región>-<sufijoOpcional>`
- **Separadores**: guion medio `-`. Evitar guiones bajos y mayúsculas.
- **Longitud**: respetar límites de cada servicio (por ejemplo, buckets ≤ 63 caracteres, BigQuery datasets ≤ 1024 caracteres, etc.).
- **Formato**: usar minúsculas; para identificadores con restricciones (BigQuery tablas, columnas) utilizar `snake_case`.
- **Entornos** estándar: `dev`, `qa`, `prod`. Se puede contemplar `sandbox` o `dr` si aplica.
- **Dominios funcionales** (ejemplos): `cli` (clientes), `opr` (operaciones), `fin` (financiero), `mkt` (marketing). Ajustar según catálogo de datos.
- **Componentes abreviados**:
  - `raw` / `stg` / `cur` / `pub`: capas de datos (bronze, silver, gold, publish).
  - `bq`, `gcs`, `spn`, `df`, `ps`, `cmp`, `sa`: BigQuery, Cloud Storage, Spanner, Dataflow, Pub/Sub, Composer, Service Account.

## Etiquetas y anotaciones

Aplicar etiquetas (`labels`) comunes en los recursos que lo permitan:

| Clave          | Valor sugerido                         | Descripción                             |
|----------------|----------------------------------------|-----------------------------------------|
| `project`      | `ing-datos-migracion-gcp`              | Proyecto paraguas                       |
| `business_unit`| `medicus-data`                         | Unidad responsable                      |
| `environment`  | `dev` \| `qa` \| `prod`                | Entorno de despliegue                   |
| `domain`       | `<dominio>`                            | Dominio de datos                        |
| `managed_by`   | `terraform` \| `manual`                | Origen del recurso                      |
| `owner`        | `data-platform`                        | Equipo responsable                      |

## Proyectos y carpetas

- **Proyectos GCP**: `medicus-data-<entorno>` (por ejemplo `medicus-data-prod`, `medicus-data-dataml-dev`).
- **Folders (opcional)**: `medicus-data/<entorno>` para organizar políticas IAM y facturación.

> **Nota:** Para el entorno dev actual se usa el proyecto `medicus-data-dataml-dev` que incluye el sufijo `-dataml` para identificar la plataforma de Data/ML.

## Almacenamiento: Cloud Storage

- **Buckets landing/raw**: `medicus-data-raw-<dominio>-<entorno>-<region>` → ej. `medicus-data-raw-cli-prod-us`
- **Buckets Bronze (con sufijo de capa)**: `medicus-data-bronze-raw-<entorno>-<region>` → ej. `medicus-data-bronze-raw-dev-uscentral1`
- **Buckets staging**: `medicus-data-stg-<dominio>-<entorno>-<region>`
- **Buckets curated/publicados**: `medicus-data-cur-<dominio>-<entorno>-<region>` y `medicus-data-pub-<dominio>-<entorno>-<region>`
- **Buckets temporales Dataflow**: `medicus-data-df-tmp-<entorno>-<region>`
- **Buckets templates Dataflow**: `medicus-data-df-tpl-<entorno>-<region>`

Reglas: los buckets son globales, validar unicidad y longitud. Para `region`, usar código corto (`us`, `us-central1`, `sa-east1`) según necesidad.

> **Formato de archivos Bronze:** Los datos en la capa Bronze se almacenan en formato **Parquet** (no CSV) para optimizar el rendimiento y compatibilidad con herramientas de Big Data.

## BigQuery

- **Datasets por capa**: `medicus_<layer>_<dominio>_<entorno>` → ej. `medicus_bronze_cli_prod`, `medicus_bronze_raw_acumulado` (para datos acumulados en dev)
- **Tablas**: `layer_dom_usuario`, usar `snake_case` (ej. `bronze_cli_historial_visitas`).
- **Views**: prefijo `vw_` (ej. `vw_cli_resumen_prod`).
- **Routines/UDFs**: prefijo `fn_`.
- **Proyectos para analytics** (si se separan): `medicus-bq-<entorno>` o `medicus-data-dataml-<entorno>` para entornos con plataforma Data/ML integrada.

> **Ejemplo dev:** El dataset `medicus_bronze_raw_acumulado` en el proyecto `medicus-data-dataml-dev` almacena datos Bronze acumulados para el entorno de desarrollo.

## Cloud Spanner

- **Instancia**: `medicus-spn-<dominio>-<entorno>` → ej. `medicus-spn-cli-prod`
- **Base de datos**: `db_<dominio>_<proposito>` → ej. `db_cli_cuentas`
- **Esquemas**: tablas en `snake_case` y columnas en `snake_case`.

## Dataflow

- **Service Account**: `sa-df-<dominio>-<entorno>@<project>.iam.gserviceaccount.com`
- **Jobs**: `df-<pipeline>-<dominio>-<entorno>` → ej. `df-bronze-to-silver-cli-prod`
- **Plantillas (GCS)**: ubicadas en `medicus-data-df-tpl-<entorno>-<region>/pipelines/<pipeline>.json`
- **Stages temporales**: `medicus-data-df-tmp-<entorno>-<region>/jobs/<pipeline>/`

## Pub/Sub

- **Topics**: `ps-<dominio>-<evento>-<entorno>` → ej. `ps-cli-alta-socio-prod`
- **Subscriptions**: `ps-<dominio>-<evento>-<consumer>-<entorno>` → ej. `ps-cli-alta-socio-df-silver-prod`

## Orquestación (Cloud Composer / Workflows)

- **Composer environment**: `cmp-data-<entorno>` → ej. `cmp-data-qa`
- **DAGs / Workflows**: `dag_<pipeline>_<dominio>_<entorno>`
- **Buckets Composer**: `medicus-data-cmp-<entorno>-<region>`

## IAM Service Accounts genéricas

- Formato: `sa-<componente>-<dominio>-<entorno>@<project>.iam.gserviceaccount.com`
- Ejemplos: `sa-bq-cli-prod`, `sa-spn-fin-qa`

## Secret Manager

- **Secretos**: `sec-<componente>-<dominio>-<entorno>-<descripcion>` → `sec-spn-cli-prod-credentials`
- **Versiones**: mantener etiqueta `stage` y `owner`.

## Artifact Registry / Contenedores

- **Repositorio**: `<region>-docker.pkg.dev/medicus-data-platform/<dominio>/<app>-<entorno>`
- **Imágenes**: `<app>-<version>` con tags semánticos.

## Cloud Logging & Monitoring

- **Logs-based metrics**: `lbm_<dominio>_<proposito>_<entorno>`
- **Alerting policies**: `alert_<dominio>_<proposito>_<entorno>`

## Ejemplo completo

Para un pipeline que ingiere información de clientes (dominio `cli`) desde sistemas legacy a capa bronze y luego a silver en `prod`:

| Recurso                        | Nombre sugerido                                         |
|--------------------------------|----------------------------------------------------------|
| Bucket landing                 | `medicus-data-raw-cli-prod-us`                           |
| Bucket staging                 | `medicus-data-stg-cli-prod-us`                           |
| Dataset BigQuery bronze        | `medicus_bronze_cli_prod`                                |
| Dataset BigQuery silver        | `medicus_silver_cli_prod`                                |
| Job Dataflow bronze→silver     | `df-bronze-to-silver-cli-prod`                           |
| Topic Pub/Sub eventos cliente  | `ps-cli-alta-socio-prod`                                 |
| Spanner instance               | `medicus-spn-cli-prod`                                   |
| Spanner database               | `db_cli_master`                                          |
| Service account Dataflow       | `sa-df-cli-prod@medicus-data-prod.iam.gserviceaccount.com` |
| Composer environment           | `cmp-data-prod`                                          |

## Ejemplo completo: Entorno Dev

Configuración actualizada para el entorno de desarrollo con los recursos confirmados:

| Recurso                        | Nombre/Valor                                             | Notas |
|--------------------------------|----------------------------------------------------------|-------|
| Proyecto GCP                   | `medicus-data-dataml-dev`                                | Proyecto para Data/ML en dev |
| Bucket Bronze                  | `medicus-data-bronze-raw-dev-uscentral1`                 | Almacena archivos Parquet raw |
| BigQuery Instance              | `medicus-data-dataml-dev`                                | Misma instancia que el proyecto |
| Dataset Bronze                 | `medicus_bronze_raw_acumulado`                           | Dataset para datos acumulados Bronze |
| Dataset completo               | `medicus-data-dataml-dev.medicus_bronze_raw_acumulado`   | Referencia completa |
| Formato archivos Bronze        | **Parquet**                                              | No CSV - estándar para Bronze |
| Job Dataflow Bronze→Silver     | `df-bronze-to-silver-data-dev`                           | Nomenclatura alineada |
| Región                         | `us-central1`                                            | Región principal |

## Ejemplo completo: Entorno Prod

1. Validar con seguridad, networking y compliance para detectar restricciones adicionales (nombres reservados, longitud).
2. Incorporar la convención en los módulos Terraform y plantillas CI/CD.
3. Mantener una matriz de dominios y owners para asegurar consistencia al crear nuevos recursos.
