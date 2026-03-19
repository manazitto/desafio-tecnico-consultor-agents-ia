"""Relatorio de avaliacao."""
from dataclasses import dataclass, field, asdict
import json
from datetime import datetime, timezone


@dataclass
class EvalReport:
    """Resultado de uma suite de evals."""
    suite: str
    total: int
    passed: int
    failed: int
    accuracy: float
    results: list[dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def summary(self) -> str:
        """Resumo legivel do relatorio."""
        return (
            f"Suite: {self.suite}\n"
            f"Total: {self.total} | Passed: {self.passed} | Failed: {self.failed}\n"
            f"Accuracy: {self.accuracy:.1%}\n"
        )
