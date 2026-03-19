"""Carregamento de datasets JSONL para evals."""
import json


def load_dataset(path: str) -> list[dict]:
    """Carrega um arquivo JSONL e retorna lista de dicts."""
    cases = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases
