"""Testes para o CreditInterviewAgent.

Requirements: INTERVIEW-01, INTERVIEW-02, INTERVIEW-04
"""
import pytest

from banco_agil.agents.credit_interview import CreditInterviewAgent


class TestCreditInterviewAgent:
    """Configuracao do agente de entrevista de credito."""

    def test_interview_has_correct_name(self):
        agent = CreditInterviewAgent()
        assert agent.name == "credit_interview"

    def test_interview_has_calculate_score_tool(self):
        agent = CreditInterviewAgent()
        tool_names = [t.name for t in agent.tools]
        assert "calculate_new_score" in tool_names

    def test_interview_system_prompt_mentions_questions(self):
        agent = CreditInterviewAgent()
        prompt = agent.system_prompt.lower()
        assert "renda" in prompt
        assert "emprego" in prompt
        assert "dependentes" in prompt
