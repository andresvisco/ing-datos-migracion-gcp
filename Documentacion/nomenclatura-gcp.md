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

### Formato de archivos en Cloud Storage

**Formato principal: Parquet**

Para la zona Bronze, el formato estándar es **Parquet** debido a sus ventajas:

- **Compresión columnar**: Reduce el tamaño de almacenamiento significativamente.
- **Lectura eficiente**: BigQuery y Dataflow pueden leer solo las columnas necesarias.
- **Preservación de tipos**: Mantiene tipos de datos nativos (int, float, timestamp, etc.).
- **Compatibilidad**: Soporte nativo en todo el stack GCP (BigQuery, Dataflow, Spark).

**Convenciones de nombres de archivos Parquet:**

- Usar particionamiento por fecha cuando sea posible: `fecha=YYYY-MM-DD/data.parquet`
- Incluir prefijo descriptivo: `{source_system}_{tabla}_{timestamp}.parquet`
- Ejemplo: `qlikview_clientes_20240115_120000.parquet`

**Formato alternativo: Avro**

Usar Avro solo cuando:
- Se requiera evolución de esquema dinámica
- Los datos provengan de streaming (Pub/Sub, Kafka)
- Exista compatibilidad legacy con sistemas existentes

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

## Ejemplo configuración entorno DEV

Configuración del entorno de desarrollo con datos exportados desde QlikView en formato Parquet:

| Recurso                        | Nombre utilizado                                         | Notas                                    |
|--------------------------------|----------------------------------------------------------|------------------------------------------|
| **Proyecto GCP**               | `medicus-data-dataml-dev`                                | Proyecto principal del entorno dev       |
| **Bucket Bronze (RAW)**        | `medicus-data-bronze-raw-dev-uscentral1`                 | Almacena archivos Parquet de QlikView    |
| **Dataset BigQuery Bronze**    | `medicus_bronze_raw_acumulado`                           | Dataset acumulado en proyecto dev        |
| **Dataset completo**           | `medicus-data-dataml-dev.medicus_bronze_raw_acumulado`   | Referencia completa para consultas       |
| **Formato de archivos**        | **Parquet**                                              | Optimizado para BigQuery y Dataflow      |
| **Job Dataflow ingesta**       | `df-qlikview-to-bronze-dev`                              | Pipeline de ingesta desde QlikView       |
| **Service Account Dataflow**   | `sa-df-bronze-dev@medicus-data-dataml-dev.iam.gserviceaccount.com` | SA para pipelines de Bronze      |
| **Composer environment**       | `cmp-data-dev`                                           | Orquestador Airflow para dev             |
| **Bucket Composer**            | `medicus-data-cmp-dev-uscentral1`                        | Bucket asociado a Composer               |

### Estructura de archivos en Bronze (DEV)

Los archivos Parquet exportados desde QlikView se organizan en el bucket Bronze siguiendo esta estructura:

```
gs://medicus-data-bronze-raw-dev-uscentral1/
├── qlikview_exports/
│   ├── tabla1/
│   │   ├── fecha=2024-01-01/
│   │   │   └── data.parquet
│   │   └── fecha=2024-01-02/
│   │       └── data.parquet
│   ├── tabla2/
│   │   └── fecha=2024-01-01/
│   │       └── data.parquet
│   └── _metadata/
│       └── export_log.json
└── staging/
    └── temp/
```

### Etiquetas aplicadas en DEV

Todos los recursos del entorno dev incluyen las siguientes etiquetas para gobernanza:

```yaml
labels:
  project: "ing-datos-migracion-gcp"
  business_unit: "medicus-data"
  environment: "dev"
  domain: "bronze-raw"
  managed_by: "terraform"
  owner: "data-platform"
  data_format: "parquet"
  source_system: "qlikview"
```

## Próximos pasos sugeridos

1. **Validación y Compliance**: Validar con seguridad, networking y compliance para detectar restricciones adicionales (nombres reservados, longitud).
2. **Integración con Terraform**: Incorporar la convención en los módulos Terraform y plantillas CI/CD para garantizar automatización completa.
3. **Matriz de Dominios**: Mantener una matriz de dominios y owners para asegurar consistencia al crear nuevos recursos.
4. **Validación Automatizada**: Ejecutar `validate_nomenclatura.py` en todos los pipelines CI/CD antes de despliegues.
5. **Documentación de Linaje**: Registrar todos los flujos de datos en Data Catalog para trazabilidad completa.
6. **Auditoría Regular**: Revisar trimestralmente el cumplimiento de nomenclatura en todos los recursos existentes.
7. **Capacitación del Equipo**: Asegurar que todos los miembros del equipo conozcan y apliquen estas convenciones.

## Principios de Gobernanza

### Máximos Estándares de Calidad

Todas las nomenclaturas y recursos deben cumplir con:

- ✅ **Consistencia**: Mismas reglas en dev, qa y prod
- ✅ **Trazabilidad**: Nombres que permitan identificar propósito, dominio y entorno
- ✅ **Automatización**: Validación en CI/CD para prevenir errores
- ✅ **Modularidad**: Estructura que facilite reutilización y mantenimiento
- ✅ **Documentación**: Cada recurso debe tener propósito y owner claramente definidos
- ✅ **Seguridad**: Nomenclatura que facilite aplicación de políticas IAM granulares

### Etiquetas Obligatorias para Gobernanza

Todos los recursos GCP **deben** incluir estas etiquetas sin excepción:

| Etiqueta | Obligatoria | Valores Permitidos | Propósito |
|----------|-------------|-------------------|-----------|
| `project` | ✅ Sí | `ing-datos-migracion-gcp` | Identificación del proyecto paraguas |
| `business_unit` | ✅ Sí | `medicus-data` | Unidad de negocio responsable |
| `environment` | ✅ Sí | `dev`, `qa`, `prod` | Entorno de despliegue |
| `domain` | ✅ Sí | `cli`, `fin`, `opr`, etc. | Dominio funcional de datos |
| `managed_by` | ✅ Sí | `terraform`, `manual` | Método de gestión del recurso |
| `owner` | ✅ Sí | `data-platform`, `{team}` | Equipo propietario |
| `data_format` | 🔶 Condicional | `parquet`, `avro`, `json` | Formato de datos (para buckets/datasets) |
| `source_system` | 🔶 Condicional | `qlikview`, `sap`, etc. | Sistema fuente (para pipelines de ingesta) |
| `cost_center` | 🔶 Opcional | Código de centro de costos | Para facturación detallada |

### Checklist de Validación

Antes de crear cualquier recurso GCP, verificar:

- [ ] El nombre cumple con el patrón `<empresa>-<plataforma>-<dominio>-<componente>-<entorno>-<region>`
- [ ] La longitud del nombre está dentro de los límites del servicio
- [ ] Se usan solo minúsculas y guiones (no guiones bajos ni mayúsculas)
- [ ] Todas las etiquetas obligatorias están presentes
- [ ] El recurso está documentado en el Data Catalog (si aplica)
- [ ] Existe un owner claramente identificado
- [ ] El recurso se crea vía Terraform (preferido) o está documentado si es manual
