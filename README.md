# 🏥 Proyecto MEDICUS: Migración Ingeniería de Datos GCP

Este repositorio contiene el código fuente, la configuración y la documentación para la implementación de la plataforma de datos del proyecto **MEDICUS**, siguiendo una arquitectura de **Data Lakehouse** basada en el modelo de zonas **Bronze-Silver-Gold** sobre Google Cloud Platform (**GCP**).

El objetivo es ingestar, procesar y transformar datos de diversas fuentes de MEDICUS, asegurando calidad, trazabilidad y gobernanza para impulsar la analítica avanzada y la toma de decisiones.

---

## 🗺️ Arquitectura de Referencia

La arquitectura se basa en el **patrón Medallion** (Bronze, Silver, Gold) y está orquestada por **Composer (Apache Airflow)**, garantizando un flujo de datos robusto, escalable y mantenible.


---

## 🛠️ Tecnologías Clave (Stack Tecnológico)

El proyecto se despliega y opera exclusivamente en **Google Cloud Platform (GCP)**, aprovechando servicios gestionados para optimizar la eficiencia operativa.

| Categoría | Servicio / Tecnología | Propósito Principal |
| :--- | :--- | :--- |
| **Orquestación** | **Composer** (Apache Airflow) | Gestión, scheduling y monitoreo de los Data Pipelines (DAGs). |
| **Ingesta / RAW** | **Cloud Storage** (Bronze Zone) | Almacenamiento de datos crudos (RAW) en formato **Parquet** (estándar Bronze). |
| **Procesamiento** | **Dataflow** / **Spark** | Transformación de datos ETL/ELT, limpieza y enriquecimiento. |
| **Data Warehouse** | **BigQuery** (Silver & Gold Zones) | Almacenamiento optimizado para el consumo, analítica y reporting. |
| **Calidad de Datos**| **Great Expectations** | Implementación de validaciones de calidad de datos en la zona Bronze. |
| **Metadatos/Catálogo** | **Data Catalog** | Descubrimiento, inventario, linaje y gestión de metadatos. |
| **Gobernanza** | **IAM, Cloud Logging, Versiones** | Seguridad, auditoría, monitoreo y control de versiones de datos. |

---

## 📂 Estructura del Repositorio

La estructura de carpetas sigue las mejores prácticas para un proyecto de Data Engineering y refleja las etapas del flujo de datos:
```plaintext
medicus-data-platform/
├── dags/                          # Definiciones de pipelines para Composer (Airflow)
│   ├── bronze_ingest_dag.py
│   ├── silver_transform_dag.py
│   └── gold_analytics_dag.py
├── dataflow_jobs/                 # Scripts de transformación para Dataflow
│   ├── bronze_validation.py
│   ├── silver_clean.py
│   └── gold_aggregation.py
├── sql/                           # Consultas y scripts DDL/DML para BigQuery
│   ├── silver_schemas/
│   └── gold_views/
├── terraform/                     # Configuración de infraestructura como código (IaC)
│   └── gcp_resources.tf
├── tests/                         # Pruebas unitarias, de integración y Great Expectations
│   └── ge_expectations.json
├── docs/                          # Documentación del proyecto (diagramas, decisiones de diseño)
└── README.md            # Documentación principal del proyecto
```

---

## 📦 Fases del Flujo de Datos (Modelo Medallion)

### 🥉 Bronze Raw Landing Zone

* **Función:** Ingesta de datos crudos *tal cual* (RAW) desde las fuentes (`MEDICUS Source`).
* **Proceso Clave:** **Dataflow** escribe el *raw data* en Cloud Storage en formato **Parquet** (estándar para capa Bronze).
* **Calidad:** Se aplica **`Great Expectations`** para validar la *integridad básica* (ej. esquema, no-nulos) *antes* del procesamiento.
* **Salida:** Datos crudos y validados en **Cloud Storage (GCS)** en formato **Parquet**.
* **Ejemplo Dev:** `gs://medicus-data-bronze-raw-dev-uscentral1/raw/*.parquet`

### 🥈 Silver Procesado Curado

* **Función:** Limpieza, enriquecimiento y aplicación de lógica de negocio inicial.
* **Proceso Clave:** **Dataflow** realiza la **Transformación** (ETL/ELT) para curar y homogeneizar los datos, leyendo archivos **Parquet** desde Bronze.
* **Salida:** Tablas limpias y curadas en **BigQuery** (`Tablas silver`).
* **Calidad:** Aplicación de chequeos de `Calidad Curado` post-transformación.
* **Ejemplo Dev:** Dataset `medicus-data-dataml-dev.medicus_bronze_raw_acumulado`

### 🥇 Gold Analítica y Reporting

* **Función:** Almacenamiento de datos listos para el consumo por usuarios de negocio, modelos de ML y herramientas de BI.
* **Proceso Clave:** Agregaciones, *joins*, creación de *features* y modelos de datos dimensionales/estrella en **BigQuery**.
* **Salida:** Tablas y vistas optimizadas para el rendimiento en **BigQuery** (`Tablas Gold`).
* **Catálogo:** Las tablas Gold son catalogadas en **Data Catalog** para su fácil descubrimiento.

---

## 🔒 Gobernanza y Control

Se han incorporado componentes de gobernanza esenciales:

* **Versionado de Datos:** Implementación de estrategias de *versionado* a nivel de *schema* y *data* para la auditabilidad.
* **Metadatos y Linaje:** Uso de **Data Catalog** para trazar el linaje de los datos desde la fuente (Bronze) hasta el consumo (Gold).
* **Seguridad y Auditoría (IAM, PII):** Aplicación de políticas de **IAM** (Identity and Access Management) y controles de acceso basados en roles. Monitoreo constante a través de **Cloud Logging**.
* **Logging & Monitoring:** Integrado en todas las zonas (Bronze, Silver, Gold) para asegurar la trazabilidad operativa de los pipelines.

---

## 🔧 Configuración de Entorno Dev

La configuración del entorno de desarrollo (`dev`) sigue estrictamente la guía de nomenclatura (ver `Documentacion/nomenclatura-gcp.md`):

| Recurso | Valor Dev | Descripción |
|---------|-----------|-------------|
| **PROJECT_ID** | `medicus-data-dataml-dev` | Proyecto GCP para entorno dev |
| **BUCKET_BRONZE** | `medicus-data-bronze-raw-dev-uscentral1` | Bucket para datos raw en formato Parquet |
| **BigQuery Instance** | `medicus-data-dataml-dev` | Instancia de BigQuery para dev |
| **Dataset Bronze** | `medicus-data-dataml-dev.medicus_bronze_raw_acumulado` | Dataset para datos acumulados Bronze |
| **Formato Bronze** | **Parquet** | Formato estándar para archivos en capa Bronze |
| **Región** | `us-central1` | Región principal para recursos dev |

> **Nota importante:** Los archivos en la capa Bronze se almacenan en formato **Parquet**, no CSV. Todos los pipelines de lectura deben usar `ReadFromParquet` en Apache Beam.

---

## ▶️ Guía Rápida de Inicio

1.  **Configuración de Entorno:**
    * Instalar `gcloud CLI`, `terraform`, y `python v3.x`.
    * Autenticarse con `gcloud auth application-default login`.
2.  **Despliegue de Infraestructura (Terraform):**
    ```bash
    cd terraform
    terraform init
    terraform plan -out=plan.tfplan
    terraform apply plan.tfplan
    ```
3.  **Despliegue de DAGs (Composer):**
    * Subir el contenido de la carpeta `dags/` al bucket de Composer.
4.  **Ejecución:**
    * Activar el DAG principal (`bronze_ingest_dag`) desde la UI de Airflow.