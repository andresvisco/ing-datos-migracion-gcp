# Integración de Nomenclatura Médicus: Terraform + Python Validator

## ¿Cómo usar?

1. **Terraform**
    - Importá el módulo `medicus_naming` desde `terraform/modules/`.
    - Usá variables dinámicas en tu pipeline (`var.dominio`, `var.entorno`, etc.).
    - Todos los recursos tendrán nomenclatura y etiquetas correctas por defecto.
    - **Ejemplo dev:** Variables para crear bucket Bronze en entorno dev:
      ```hcl
      empresa    = "medicus"
      plataforma = "data"
      dominio    = "bronze"
      componente = "raw"
      entorno    = "dev"
      region     = "uscentral1"
      ```
      Resultado: `medicus-data-bronze-raw-dev-uscentral1`

2. **Python Validator**
    - Ejecutá `tools/validate_nomenclatura.py` antes del `terraform apply`.
    - Integra el script en `.gitlab-ci.yml` o tu pipeline de CI/CD.
    - Si hay errores, el pipeline falla y previene despliegues incorrectos.
    - El validador incluye ejemplos del entorno dev actualizado.

## Ejemplo de integración en CI/CD (GitLab)

```yaml
stages:
  - validate
  - deploy

validate_naming:
  stage: validate
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - python tools/validate_nomenclatura.py
  only:
    - merge_requests
    - main

terraform_deploy:
  stage: deploy
  image: hashicorp/terraform:1.3.7
  script:
    - terraform init
    - terraform apply -auto-approve
  only:
    - main
```

---

## Recomendaciones

- Versioná el validador y el módulo de nomenclatura.
- Documentá todos los dominios y owners en un archivo `matriz_nomenclatura.md`.
- Usá pruebas unitarias para el validador Python (`pytest`).
- Validá siempre con equipos de seguridad y compliance.
- **Formato de datos Bronze:** Recordá que todos los archivos en capa Bronze deben estar en formato **Parquet** (no CSV), según estándar definido.

---

**Esta integración garantiza calidad, gobernanza y trazabilidad real en la plataforma de datos Médicus.**