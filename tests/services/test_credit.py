"""Testes para o servico de credito.

Requirements: CREDIT-01, CREDIT-02, CREDIT-03, CREDIT-04
"""
import csv
import os
import pytest
from unittest.mock import patch
from datetime import datetime

from banco_agil.services.credit import CreditService
from banco_agil.models.cliente import Cliente


@pytest.fixture
def cliente_high_score():
    """Cliente com score alto (permite limite ate 30000)."""
    return Cliente(
        cpf="12345678900",
        nome="Maria Silva",
        data_nascimento="1990-05-15",
        score_credito=720,
        limite_credito=15000.00,
    )


@pytest.fixture
def cliente_low_score():
    """Cliente com score baixo (permite limite ate 5000)."""
    return Cliente(
        cpf="98765432100",
        nome="Joao Santos",
        data_nascimento="1985-11-20",
        score_credito=350,
        limite_credito=3000.00,
    )


@pytest.fixture
def score_limite_data():
    """Tabela de faixas score -> limite."""
    return [
        {"score_minimo": "0", "score_maximo": "299", "limite_maximo": "1000"},
        {"score_minimo": "300", "score_maximo": "499", "limite_maximo": "5000"},
        {"score_minimo": "500", "score_maximo": "699", "limite_maximo": "15000"},
        {"score_minimo": "700", "score_maximo": "849", "limite_maximo": "30000"},
        {"score_minimo": "850", "score_maximo": "1000", "limite_maximo": "50000"},
    ]


@pytest.fixture
def credit_service(score_limite_data, tmp_path):
    """CreditService com dados mockados."""
    solicitacoes_path = str(tmp_path / "solicitacoes.csv")
    with patch("banco_agil.services.credit.read_csv", return_value=score_limite_data):
        service = CreditService(
            score_limite_path="fake_path.csv",
            solicitacoes_path=solicitacoes_path,
        )
    return service


class TestCreditQuery:
    """CREDIT-01: Consulta de limite de credito."""

    def test_get_credit_limit_returns_current_limit(self, credit_service, cliente_high_score):
        """Retorna o limite atual do cliente."""
        limite = credit_service.get_credit_limit(cliente_high_score)
        assert limite == 15000.00


class TestCreditIncrease:
    """CREDIT-02/03/04: Solicitacao de aumento de limite."""

    def test_request_increase_creates_csv_record(self, credit_service, cliente_high_score):
        """Solicitacao de aumento gera registro no CSV."""
        credit_service.request_increase(cliente_high_score, 25000.00)
        assert os.path.exists(credit_service.solicitacoes_path)
        with open(credit_service.solicitacoes_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 1

    def test_request_increase_record_has_correct_columns(self, credit_service, cliente_high_score):
        """Registro no CSV tem todas as colunas obrigatorias."""
        credit_service.request_increase(cliente_high_score, 25000.00)
        with open(credit_service.solicitacoes_path) as f:
            reader = csv.DictReader(f)
            row = next(reader)
        required_columns = {
            "cpf_cliente",
            "data_hora_solicitacao",
            "limite_atual",
            "novo_limite_solicitado",
            "status_pedido",
        }
        assert required_columns.issubset(set(row.keys()))
        datetime.fromisoformat(row["data_hora_solicitacao"])

    def test_request_increase_approved_when_score_sufficient(self, credit_service, cliente_high_score):
        """Score 720 permite ate 30000 -> solicitacao de 25000 aprovada."""
        result = credit_service.request_increase(cliente_high_score, 25000.00)
        assert result.status == "aprovado"

    def test_request_increase_rejected_when_score_insufficient(self, credit_service, cliente_low_score):
        """Score 350 permite ate 5000 -> solicitacao de 10000 rejeitada."""
        result = credit_service.request_increase(cliente_low_score, 10000.00)
        assert result.status == "rejeitado"

    def test_request_increase_negative_amount_rejected(self, credit_service, cliente_high_score):
        """Solicitacao com valor negativo ou zero deve ser rejeitada."""
        with pytest.raises(ValueError):
            credit_service.request_increase(cliente_high_score, -1000.00)
