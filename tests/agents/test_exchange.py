"""Testes para o ExchangeAgent.

Requirements: EXCHANGE-01, EXCHANGE-02
"""
import pytest

from banco_agil.agents.exchange import ExchangeAgent


class TestExchangeAgent:
    """Configuracao do agente de cambio."""

    def test_exchange_has_correct_name(self):
        agent = ExchangeAgent()
        assert agent.name == "exchange"

    def test_exchange_has_fetch_rate_tool(self):
        agent = ExchangeAgent()
        tool_names = [t.name for t in agent.tools]
        assert "fetch_exchange_rate" in tool_names

    def test_exchange_has_end_conversation_tool(self):
        agent = ExchangeAgent()
        tool_names = [t.name for t in agent.tools]
        assert "end_conversation" in tool_names
