"""Testes para o servico de calculo de score.

Requirements: INTERVIEW-02, INTERVIEW-03
"""
import pytest
from unittest.mock import patch, MagicMock

from banco_agil.services.score import ScoreService


class TestScoreCalculation:
    """INTERVIEW-02: Calculo de score com formula ponderada."""

    def test_calculate_score_formal_no_debts(self):
        """Emprego formal, sem dividas, renda alta -> score alto."""
        service = ScoreService()
        score = service.calculate(
            renda_mensal=10000.0,
            tipo_emprego="formal",
            despesas_fixas=3000.0,
            num_dependentes=1,
            tem_dividas=False,
        )
        assert 0 <= score <= 1000
        assert score > 500

    def test_calculate_score_unemployed_with_debts(self):
        """Desempregado, com dividas, muitos dependentes -> score baixo."""
        service = ScoreService()
        score = service.calculate(
            renda_mensal=0.0,
            tipo_emprego="desempregado",
            despesas_fixas=500.0,
            num_dependentes=3,
            tem_dividas=True,
        )
        assert 0 <= score <= 1000
        assert score < 200

    def test_calculate_score_clamped_to_0_1000(self):
        """Score deve ser clamped entre 0 e 1000 independente dos inputs."""
        service = ScoreService()
        score_high = service.calculate(
            renda_mensal=100000.0,
            tipo_emprego="formal",
            despesas_fixas=0.0,
            num_dependentes=0,
            tem_dividas=False,
        )
        assert score_high <= 1000

        score_low = service.calculate(
            renda_mensal=0.0,
            tipo_emprego="desempregado",
            despesas_fixas=10000.0,
            num_dependentes=3,
            tem_dividas=True,
        )
        assert score_low >= 0

    def test_calculate_score_autonomous_worker(self):
        """Autonomo com renda moderada -> score medio."""
        service = ScoreService()
        score = service.calculate(
            renda_mensal=5000.0,
            tipo_emprego="autonomo",
            despesas_fixas=2000.0,
            num_dependentes=2,
            tem_dividas=False,
        )
        assert 0 <= score <= 1000
        assert 200 < score < 800


class TestScoreUpdate:
    """INTERVIEW-03: Atualizacao de score no CSV."""

    def test_update_score_persists_to_csv(self, tmp_path):
        """Score atualizado deve ser persistido no clientes.csv."""
        csv_path = str(tmp_path / "clientes.csv")
        import csv

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["cpf", "nome", "data_nascimento", "score_credito", "limite_credito"],
            )
            writer.writeheader()
            writer.writerow({
                "cpf": "12345678900",
                "nome": "Maria Silva",
                "data_nascimento": "1990-05-15",
                "score_credito": "450",
                "limite_credito": "5000.00",
            })

        service = ScoreService()
        service.update_score(csv_path, cpf="12345678900", new_score=750)

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            row = next(reader)
        assert int(row["score_credito"]) == 750
