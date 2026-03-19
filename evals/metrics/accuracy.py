"""Metricas de accuracy para evals."""


def exact_match_accuracy(results: list[dict]) -> float:
    """Calcula accuracy por match exato entre expected e actual."""
    if not results:
        return 0.0
    matches = sum(1 for r in results if r["expected"] == r["actual"])
    return matches / len(results)


def contains_match_accuracy(results: list[dict]) -> float:
    """Calcula accuracy verificando se expected esta contido em actual."""
    if not results:
        return 0.0
    matches = sum(
        1 for r in results
        if r["expected"].lower() in r["actual"].lower()
    )
    return matches / len(results)
