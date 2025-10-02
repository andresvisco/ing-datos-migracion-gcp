import re
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)

def validar_nombre_recurso(
    nombre: str, 
    tipo: str, 
    longitud_max: int
) -> Tuple[bool, str]:
    """
    Valida la nomenclatura de un recurso según tipo y longitud máxima.
    """
    patron = r"^[a-z0-9\-]{1,%d}$" % longitud_max
    if not re.match(patron, nombre):
        return False, f"Nombre inválido: {nombre}. Debe ser minúsculas, números y guiones, máx {longitud_max} caracteres."
    if "_" in nombre or nombre.lower() != nombre:
        return False, f"Evitar guiones bajos y mayúsculas en: {nombre}"
    if len(nombre) > longitud_max:
        return False, f"El nombre excede la longitud permitida ({longitud_max})"
    return True, "OK"

def validar_etiquetas(labels: Dict[str, str]) -> List[str]:
    """
    Valida que las etiquetas obligatorias estén presentes y correctas.
    """
    requeridas = ["project", "business_unit", "environment", "domain", "managed_by", "owner"]
    errores = []
    for k in requeridas:
        if k not in labels:
            errores.append(f"Falta etiqueta obligatoria: {k}")
    return errores

if __name__ == "__main__":
    # Ejemplos de validación con recursos del entorno dev
    # Siguiendo la guía de nomenclatura-gcp.md
    
    # Validar bucket Bronze Raw del entorno dev
    nombre_bucket = "medicus-data-bronze-raw-dev-uscentral1"
    es_valido, motivo = validar_nombre_recurso(nombre_bucket, "bucket", 63)
    logging.info(f"Validación bucket Bronze dev: {es_valido}, {motivo}")

    # Ejemplo de etiquetas para recursos del entorno dev
    etiquetas = {
        "project": "ing-datos-migracion-gcp",
        "business_unit": "medicus-data",
        "environment": "dev",  # Entorno de desarrollo
        "domain": "bronze",     # Dominio de datos Bronze Raw
        "managed_by": "terraform",
        "owner": "data-platform"
    }
    errores_labels = validar_etiquetas(etiquetas)
    if errores_labels:
        logging.warning(f"Errores en etiquetas: {errores_labels}")
    else:
        logging.info("Etiquetas OK")