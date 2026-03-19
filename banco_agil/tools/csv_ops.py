"""Operacoes de leitura e escrita em CSV."""
import csv
import os


def read_csv(path: str) -> list[dict]:
    """Le um CSV e retorna lista de dicionarios."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def append_csv_row(path: str, row: dict) -> None:
    """Adiciona uma linha ao final de um CSV existente."""
    file_exists = os.path.exists(path)
    write_header = not file_exists or os.path.getsize(path) == 0

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def update_csv_row(path: str, key_column: str, key_value: str, updates: dict) -> None:
    """Atualiza uma linha especifica de um CSV identificada por chave."""
    rows = read_csv(path)
    fieldnames = rows[0].keys() if rows else []

    updated = False
    for row in rows:
        if row[key_column] == key_value:
            row.update(updates)
            updated = True

    if not updated:
        raise ValueError(f"Registro com {key_column}={key_value} nao encontrado")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
