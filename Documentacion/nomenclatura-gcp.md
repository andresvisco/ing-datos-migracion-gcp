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

- **Proyectos GCP**: `medicus-data-<entorno>` (por ejemplo `medicus-data-prod`).
- **Folders (opcional)**: `medicus-data/<entorno>` para organizar políticas IAM y facturación.

## Almacenamiento: Cloud Storage

- **Buckets landing/raw**: `medicus-data-raw-<dominio>-<entorno>-<region>` → ej. `medicus-data-raw-cli-prod-us`
- **Buckets staging**: `medicus-data-stg-<dominio>-<entorno>-<region>`
- **Buckets curated/publicados**: `medicus-data-cur-<dominio>-<entorno>-<region>` y `medicus-data-pub-<dominio>-<entorno>-<region>`
- **Buckets temporales Dataflow**: `medicus-data-df-tmp-<entorno>-<region>`
- **Buckets templates Dataflow**: `medicus-data-df-tpl-<entorno>-<region>`

Reglas: los buckets son globales, validar unicidad y longitud. Para `region`, usar código corto (`us`, `us-central1`, `sa-east1`) según necesidad.

### Formato de archivos recomendado

Para la zona **Bronze Raw Landing Zone**, se recomienda utilizar formato **Parquet** en lugar de CSV por los siguientes beneficios:

- **Almacenamiento optimizado:** Compresión columnar que reduce significativamente el espacio de almacenamiento
- **Rendimiento de consultas:** Lectura eficiente al permitir leer solo las columnas necesarias
- **Tipos de datos estructurados:** Preserva esquemas y tipos de datos nativos
- **Compatibilidad:** Ampliamente soportado por Dataflow, BigQuery, Spark y herramientas de Big Data

**Ejemplo:** Los archivos en `gs://medicus-data-bronze-raw-dev-uscentral1/raw/*.parquet` siguen esta práctica recomendada.

## BigQuery

- **Datasets por capa**: `medicus_<layer>_<dominio>_<entorno>` → ej. `medicus_bronze_cli_prod`
- **Tablas**: `layer_dom_usuario`, usar `snake_case` (ej. `bronze_cli_historial_visitas`).
- **Views**: prefijo `vw_` (ej. `vw_cli_resumen_prod`).
- **Routines/UDFs**: prefijo `fn_`.
- **Proyectos para analytics** (si se separan): `medicus-bq-<entorno>`.

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

### Entorno Producción (prod)

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

### Entorno Desarrollo (dev)

Recursos configurados para el entorno de desarrollo siguiendo la misma convención:

| Recurso                        | Nombre configurado                                       |
|--------------------------------|----------------------------------------------------------|
| Proyecto GCP                   | `medicus-data-dataml-dev`                                |
| Bucket Bronze Raw              | `medicus-data-bronze-raw-dev-uscentral1`                 |
| Dataset BigQuery Bronze        | `medicus_bronze_raw_acumulado` (en `medicus-data-dataml-dev`) |
| Dataset BigQuery Silver        | `medicus_silver_curated` (en `medicus-data-dataml-dev`)  |
| Job Dataflow bronze→silver     | `df-bronze-to-silver-dev`                                |
| Región                         | `us-central1`                                            |
| Formato archivos Bronze        | `Parquet` (optimizado para almacenamiento y consultas)   |

**Nota:** El entorno dev utiliza el proyecto `medicus-data-dataml-dev` que sigue el patrón `medicus-data-<entorno>`, con recursos alineados a las convenciones de nomenclatura establecidas.

## Próximos pasos sugeridos

1. Validar con seguridad, networking y compliance para detectar restricciones adicionales (nombres reservados, longitud).
2. Incorporar la convención en los módulos Terraform y plantillas CI/CD.
3. Mantener una matriz de dominios y owners para asegurar consistencia al crear nuevos recursos.
