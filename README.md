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
| **Ingesta / RAW** | **Cloud Storage** (Bronze Zone) | Almacenamiento de datos crudos (RAW) en formato **Parquet** (principal) y Avro. |
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

* **Función:** Ingesta de datos crudos *tal cual* (RAW) desde las fuentes (`MEDICUS Source`), incluyendo exportaciones desde **QlikView**.
* **Proceso Clave:** **Dataflow** escribe el *raw data* en Cloud Storage en formato **Parquet** (formato principal, con soporte para Avro cuando sea necesario).
* **Formato Estándar:** **Parquet** - Formato columnar optimizado que ofrece compresión eficiente, lectura selectiva y compatibilidad nativa con BigQuery y Dataflow.
* **Calidad:** Se aplica **`Great Expectations`** para validar la *integridad básica* (ej. esquema, no-nulos, tipos de datos) *antes* del procesamiento.
* **Salida:** Datos crudos y validados en **Cloud Storage (GCS)** listos para transformación a Silver.
* **Ejemplo DEV:** `gs://medicus-data-bronze-raw-dev-uscentral1/qlikview_exports/*.parquet`

### 🥈 Silver Procesado Curado

* **Función:** Limpieza, enriquecimiento y aplicación de lógica de negocio inicial.
* **Proceso Clave:** **Dataflow** realiza la **Transformación** (ETL/ELT) para curar y homogeneizar los datos.
* **Salida:** Tablas limpias y curadas en **BigQuery** (`Tablas silver`).
* **Calidad:** Aplicación de chequeos de `Calidad Curado` post-transformación.

### 🥇 Gold Analítica y Reporting

* **Función:** Almacenamiento de datos listos para el consumo por usuarios de negocio, modelos de ML y herramientas de BI.
* **Proceso Clave:** Agregaciones, *joins*, creación de *features* y modelos de datos dimensionales/estrella en **BigQuery**.
* **Salida:** Tablas y vistas optimizadas para el rendimiento en **BigQuery** (`Tablas Gold`).
* **Catálogo:** Las tablas Gold son catalogadas en **Data Catalog** para su fácil descubrimiento.

---

## 🔒 Gobernanza y Control

Se han incorporado componentes de gobernanza esenciales para cumplir con los **máximos estándares de calidad, trazabilidad y modularidad**:

* **Nomenclatura Estandarizada:** Convenciones rigurosas para nombres de recursos, datasets y buckets siguiendo la guía `nomenclatura-gcp.md`.
* **Etiquetado Obligatorio:** Todos los recursos GCP incluyen etiquetas (`labels`) para trazabilidad: `project`, `business_unit`, `environment`, `domain`, `managed_by`, `owner`.
* **Versionado de Datos:** Implementación de estrategias de *versionado* a nivel de *schema* y *data* para la auditabilidad y reproducibilidad.
* **Metadatos y Linaje:** Uso de **Data Catalog** para trazar el linaje de los datos desde la fuente (Bronze) hasta el consumo (Gold), garantizando trazabilidad completa.
* **Seguridad y Auditoría (IAM, PII):** Aplicación de políticas de **IAM** (Identity and Access Management) y controles de acceso basados en roles. Monitoreo constante a través de **Cloud Logging**.
* **Logging & Monitoring:** Integrado en todas las zonas (Bronze, Silver, Gold) para asegurar la trazabilidad operativa de los pipelines y facilitar la depuración.
* **Modularidad:** Arquitectura basada en módulos Terraform reutilizables que garantizan consistencia y facilitan el mantenimiento.
* **Validación Automatizada:** Scripts de validación de nomenclatura (`validate_nomenclatura.py`) integrados en CI/CD para prevenir despliegues no conformes.

### 📋 Estándares de Calidad

Todos los recursos y procesos siguen estos principios:

1. **Consistency**: Nomenclatura uniforme en todos los entornos (dev, qa, prod).
2. **Traceability**: Linaje completo de datos desde ingesta hasta consumo.
3. **Security**: Principio de privilegio mínimo y encriptación end-to-end.
4. **Maintainability**: Código modular, documentado y versionado.
5. **Scalability**: Diseño que permite crecimiento horizontal sin refactorización mayor.

---

## 🔧 Configuración del Entorno de Desarrollo (DEV)

El entorno de desarrollo (`dev`) se encuentra configurado con los siguientes parámetros de infraestructura:

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| **PROJECT_ID** | `medicus-data-dataml-dev` | Proyecto GCP para el entorno de desarrollo |
| **BUCKET_BRONZE** | `medicus-data-bronze-raw-dev-uscentral1` | Bucket de almacenamiento para datos crudos (Bronze Zone) |
| **BigQuery Instance** | `medicus-data-dataml-dev` | Instancia de BigQuery para procesamiento y análisis |
| **Dataset Bronze** | `medicus-data-dataml-dev.medicus_bronze_raw_acumulado` | Dataset acumulado de datos crudos en BigQuery |
| **Formato de Archivos Bronze** | **Parquet** | Archivos exportados desde QlikView en formato Parquet |

### 📊 Flujo de Datos en DEV

Los datos en el entorno de desarrollo siguen este flujo:

1. **Exportación desde QlikView**: Los datos se exportan desde QlikView en formato **Parquet** para optimizar el almacenamiento y rendimiento.
2. **Ingesta a Bronze Zone**: Los archivos Parquet se cargan al bucket `medicus-data-bronze-raw-dev-uscentral1`.
3. **Validación de Calidad**: Se ejecutan validaciones con **Great Expectations** sobre los archivos Parquet.
4. **Carga a BigQuery Bronze**: Los datos validados se cargan al dataset `medicus_bronze_raw_acumulado` en el proyecto `medicus-data-dataml-dev`.
5. **Transformación a Silver/Gold**: Los pipelines de Dataflow procesan los datos hacia las capas Silver y Gold según las reglas de negocio.

### 🎯 Formato Parquet: Ventajas

El uso de **Parquet** como formato estándar en la zona Bronze ofrece:

- **Compresión eficiente**: Reducción del espacio de almacenamiento hasta 10x comparado con formatos de texto.
- **Lectura columnar**: Optimización de consultas que acceden solo a columnas específicas.
- **Compatibilidad**: Integración nativa con BigQuery, Dataflow, Spark y otras herramientas del ecosistema GCP.
- **Preservación de tipos**: Mantenimiento de la integridad de los tipos de datos originales.
- **Metadatos embebidos**: Esquema y estadísticas incluidos en el archivo para mejor catalogación.

---

## ▶️ Guía Rápida de Inicio

1.  **Configuración de Entorno:**
    * Instalar `gcloud CLI`, `terraform`, y `python v3.x`.
    * Autenticarse con `gcloud auth application-default login`.
    * Configurar el proyecto por defecto: `gcloud config set project medicus-data-dataml-dev`
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