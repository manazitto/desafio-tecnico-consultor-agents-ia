"""Testes para o client de API de cambio.

Requirements: EXCHANGE-01
"""
import pytest
from unittest.mock import patch, MagicMock

from banco_agil.tools.exchange_api import fetch_exchange_rate


class TestExchangeApi:
    """EXCHANGE-01: Consulta de cotacao de moedas."""

    def test_fetch_exchange_rate_returns_float(self):
        """Cotacao retornada deve ser um float positivo."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"USDBRL": {"bid": "5.25"}}

        with patch("banco_agil.tools.exchange_api.httpx.get", return_value=mock_response):
            rate = fetch_exchange_rate("USD", "BRL")
        assert isinstance(rate, float)
        assert rate > 0

    def test_fetch_exchange_rate_api_unavailable(self):
        """API indisponivel deve levantar excecao controlada."""
        with patch("banco_agil.tools.exchange_api.httpx.get", side_effect=ConnectionError("API offline")):
            with pytest.raises(ConnectionError):
                fetch_exchange_rate("USD", "BRL")
