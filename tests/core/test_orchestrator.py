"""Testes para o orquestrador de agentes.

Requirements: ROUTE-01
"""
import pytest
from unittest.mock import MagicMock

from banco_agil.core.orchestrator import Orchestrator


class TestOrchestrator:
    """ROUTE-01: Roteamento baseado em intencao."""

    @pytest.fixture
    def orchestrator(self):
        """Orquestrador com agentes mockados."""
        orch = Orchestrator()
        orch.register_agent("credit", MagicMock())
        orch.register_agent("exchange", MagicMock())
        orch.register_agent("credit_interview", MagicMock())
        return orch

    def test_orchestrator_routes_credit_intent(self, orchestrator):
        """Intencao de credito deve rotear para agente de credito."""
        agent_name = orchestrator.resolve_agent("quero ver meu limite de credito")
        assert agent_name == "credit"

    def test_orchestrator_routes_exchange_intent(self, orchestrator):
        """Intencao de cambio deve rotear para agente de cambio."""
        agent_name = orchestrator.resolve_agent("qual a cotacao do dolar hoje")
        assert agent_name == "exchange"
