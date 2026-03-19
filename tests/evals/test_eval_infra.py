"""Testes para a infraestrutura de evals.

Requirements: EVAL-01, EVAL-02, EVAL-03, EVAL-04
"""
import json
import pytest

from evals.datasets.loader import load_dataset
from evals.metrics.accuracy import exact_match_accuracy, contains_match_accuracy
from evals.runners.single_turn import SingleTurnRunner
from evals.report import EvalReport


class TestDatasetLoader:
    """Carregamento de datasets JSONL."""

    def test_load_dataset_returns_list_of_dicts(self, tmp_path):
        """Dataset JSONL eh carregado como lista de dicts."""
        ds_path = tmp_path / "test.jsonl"
        ds_path.write_text(
            '{"input": "oi", "expected": "triage"}\n'
            '{"input": "limite", "expected": "credit"}\n'
        )
        cases = load_dataset(str(ds_path))
        assert len(cases) == 2
        assert cases[0]["input"] == "oi"

    def test_load_dataset_empty_file(self, tmp_path):
        """Dataset vazio retorna lista vazia."""
        ds_path = tmp_path / "empty.jsonl"
        ds_path.write_text("")
        cases = load_dataset(str(ds_path))
        assert cases == []


class TestMetrics:
    """Metricas de avaliacao."""

    def test_exact_match_accuracy_perfect(self):
        """100% quando todos os resultados batem."""
        results = [
            {"expected": "credit", "actual": "credit"},
            {"expected": "exchange", "actual": "exchange"},
        ]
        assert exact_match_accuracy(results) == 1.0

    def test_exact_match_accuracy_partial(self):
        """50% quando metade bate."""
        results = [
            {"expected": "credit", "actual": "credit"},
            {"expected": "exchange", "actual": "credit"},
        ]
        assert exact_match_accuracy(results) == 0.5

    def test_exact_match_accuracy_empty(self):
        """0% para lista vazia."""
        assert exact_match_accuracy([]) == 0.0

    def test_contains_match_accuracy(self):
        """Verifica se expected esta contido no actual."""
        results = [
            {"expected": "aprovado", "actual": "Sua solicitacao foi aprovado com sucesso"},
            {"expected": "rejeitado", "actual": "Infelizmente nao foi possivel aprovar"},
        ]
        assert contains_match_accuracy(results) == 0.5


class TestEvalReport:
    """Relatorio de avaliacao."""

    def test_report_has_required_fields(self):
        """Relatorio contem suite, accuracy e resultados."""
        report = EvalReport(
            suite="routing",
            total=10,
            passed=8,
            failed=2,
            accuracy=0.8,
            results=[],
        )
        assert report.suite == "routing"
        assert report.accuracy == 0.8
        assert report.total == 10

    def test_report_to_dict(self):
        """Relatorio pode ser serializado para dict/JSON."""
        report = EvalReport(
            suite="routing",
            total=2,
            passed=2,
            failed=0,
            accuracy=1.0,
            results=[{"input": "x", "expected": "y", "actual": "y", "pass": True}],
        )
        d = report.to_dict()
        assert d["suite"] == "routing"
        assert d["accuracy"] == 1.0
        assert len(d["results"]) == 1
