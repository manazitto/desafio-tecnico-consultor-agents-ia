"""Testes para o TriageAgent.

Requirements: AUTH-01, AUTH-06, ROUTE-01
"""
import pytest

from banco_agil.agents.triage import TriageAgent


class TestTriageAgent:
    """Configuracao do agente de triagem."""

    def test_triage_has_correct_name(self):
        agent = TriageAgent()
        assert agent.name == "triage"

    def test_triage_system_prompt_mentions_authentication(self):
        agent = TriageAgent()
        prompt = agent.system_prompt.lower()
        assert "cpf" in prompt
        assert "nascimento" in prompt

    def test_triage_has_authenticate_tool(self):
        agent = TriageAgent()
        tool_names = [t.name for t in agent.tools]
        assert "authenticate_client" in tool_names

    def test_triage_has_route_tool(self):
        agent = TriageAgent()
        tool_names = [t.name for t in agent.tools]
        assert "route_to_agent" in tool_names

    def test_triage_has_end_conversation_tool(self):
        agent = TriageAgent()
        tool_names = [t.name for t in agent.tools]
        assert "end_conversation" in tool_names
