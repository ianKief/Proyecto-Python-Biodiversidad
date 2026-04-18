"""
Módulo de registro de operaciones sobre datasets.

Este módulo centraliza la escritura en el archivo logs/operations.log
con el formato:

YYYY-MM-DD HH:MM:SS | dataset_name | OPERATION | N registros | STATUS(opcional)

Ejemplos rápidos:
    # Registro exitoso
    log("dataset_a1", "INSERT", 3)

    # Error sin registros afectados
    log_error("dataset_b2", "UPDATE")
"""

from datetime import datetime
from pathlib import Path
from typing import Literal

OperationType = Literal["INSERT", "UPDATE", "DELETE"]
OperationStatus = str | None

MODULE_PATH = Path(__file__).resolve()
SRC_DIR = MODULE_PATH.parent
PROJECT_ROOT = SRC_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOGS_DIR / "operations.log"

def _current_timestamp() -> str:
    """Retorna la fecha y hora actual en un formato legible.
    
    Returns:
        str: Fecha y hora actual formateada como "YYYY-MM-DD HH:MM:SS".
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _escape_log_entry(value: str | None) -> str:
    """Escapa caracteres problemáticos en una entrada de log.

    Args:
        value: El valor a escapar.

    Returns:
        str: El valor escapado, con saltos de línea reemplazados
        por espacios, tuberías eliminadas y espacios extra recortados.
    """
    if value is None:
        return ""

    cleaned = value.strip()
    for old, new in (("\n", " "), ("\r", " "), ("|", "")):
        cleaned = cleaned.replace(old, new)
    return cleaned

def _validate_records_count(records_count: object) -> int:
    if isinstance(records_count, bool) or not isinstance(records_count, int):
        raise TypeError("records_count debe ser un entero.")
    if records_count < 0:
        raise ValueError("records_count no puede ser negativo.")
    return records_count

def log(
    dataset: str,
    operation: OperationType,
    records_count: int,
    operation_status: OperationStatus = None
) -> None:
    """Registra una operación en el archivo de logs.

    Args:
        dataset: Nombre del dataset afectado.
        operation: Tipo de operación realizada (INSERT, UPDATE, DELETE).
        records_count: Cantidad de registros afectados por la operación.
        operation_status: Estado de la operación (opcional).
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    dataset = _escape_log_entry(dataset)
    if not dataset:
        raise ValueError("dataset es obligatorio.")

    if operation not in ("INSERT", "UPDATE", "DELETE"):
        raise ValueError("operation debe ser INSERT, UPDATE o DELETE.")

    entry_line = " | ".join(
        [item for item in [
            _current_timestamp(),
            dataset,
            operation,
            f"{_validate_records_count(records_count)} registros",
            _escape_log_entry(operation_status)
        ] if item]
    ) + "\n"

    with LOG_FILE_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(entry_line)

def log_error(dataset: str, operation: OperationType) -> None:
    """Registra una operación fallida sin registros afectados.

    Args:
        dataset: Nombre del dataset afectado.
        operation: Tipo de operación realizada (INSERT, UPDATE, DELETE).
    """
    log(dataset, operation, 0, "ERROR")
