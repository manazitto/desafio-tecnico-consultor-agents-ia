"""Testes para o CreditAgent.

Requirements: CREDIT-01, CREDIT-02, CREDIT-05
"""
import pytest

from banco_agil.agents.credit import CreditAgent


class TestCreditAgent:
    """Configuracao do agente de credito."""

    def test_credit_has_correct_name(self):
        agent = CreditAgent()
        assert agent.name == "credit"

    def test_credit_has_query_limit_tool(self):
        agent = CreditAgent()
        tool_names = [t.name for t in agent.tools]
        assert "query_credit_limit" in tool_names

    def test_credit_has_request_increase_tool(self):
        agent = CreditAgent()
        tool_names = [t.name for t in agent.tools]
        assert "request_credit_increase" in tool_names

    def test_credit_has_route_to_interview_tool(self):
        agent = CreditAgent()
        tool_names = [t.name for t in agent.tools]
        assert "route_to_agent" in tool_names
