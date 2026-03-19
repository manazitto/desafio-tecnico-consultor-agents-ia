"""Testes para o modelo Solicitacao.

Requirements: CREDIT-02
"""
import pytest
from datetime import datetime

from banco_agil.models.solicitacao import Solicitacao


class TestSolicitacao:
    """Modelo Solicitacao de aumento de limite."""

    def test_solicitacao_has_required_fields(self):
        """Solicitacao deve ter todos os campos obrigatorios."""
        sol = Solicitacao(
            cpf_cliente="12345678900",
            limite_atual=15000.00,
            novo_limite_solicitado=25000.00,
            status_pedido="pendente",
        )
        assert sol.cpf_cliente == "12345678900"
        assert sol.limite_atual == 15000.00
        assert sol.novo_limite_solicitado == 25000.00
        assert sol.status_pedido == "pendente"
        assert sol.data_hora_solicitacao is not None

    def test_solicitacao_timestamp_is_iso8601(self):
        """Timestamp da solicitacao deve ser ISO 8601 valido."""
        sol = Solicitacao(
            cpf_cliente="12345678900",
            limite_atual=15000.00,
            novo_limite_solicitado=25000.00,
            status_pedido="pendente",
        )
        parsed = datetime.fromisoformat(sol.data_hora_solicitacao)
        assert isinstance(parsed, datetime)
