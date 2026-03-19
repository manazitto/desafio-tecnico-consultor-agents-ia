"""Testes para o BaseAgent e sistema de tools.

Requirements: GUARD-01, ROUTE-02
"""
import pytest

from banco_agil.core.agent.base import BaseAgent, Tool, HandoffSignal


class DummyAgent(BaseAgent):
    """Agente fake para testes."""

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def system_prompt(self) -> str:
        return "Voce eh um agente de teste."

    @property
    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="dummy_tool",
                description="Ferramenta de teste",
                parameters={"type": "object", "properties": {"x": {"type": "string"}}},
                handler=lambda x: f"resultado: {x}",
            )
        ]


class TestBaseAgent:
    """Testes do contrato BaseAgent."""

    def test_agent_has_name(self):
        agent = DummyAgent()
        assert agent.name == "dummy"

    def test_agent_has_system_prompt(self):
        agent = DummyAgent()
        assert len(agent.system_prompt) > 0

    def test_agent_has_tools(self):
        agent = DummyAgent()
        assert len(agent.tools) == 1
        assert agent.tools[0].name == "dummy_tool"

    def test_tool_generates_json_schema(self):
        agent = DummyAgent()
        schema = agent.tools[0].to_schema()
        assert schema["name"] == "dummy_tool"
        assert "description" in schema
        assert "parameters" in schema

    def test_tool_handler_executes(self):
        agent = DummyAgent()
        result = agent.tools[0].handler("hello")
        assert result == "resultado: hello"

    def test_agent_get_tools_map(self):
        agent = DummyAgent()
        tools_map = agent.get_tools_map()
        assert "dummy_tool" in tools_map
        assert callable(tools_map["dummy_tool"])


class TestHandoffSignal:
    """Testes do mecanismo de handoff entre agentes."""

    def test_handoff_signal_has_target(self):
        signal = HandoffSignal(target_agent="credit", context={"cpf": "123"})
        assert signal.target_agent == "credit"
        assert signal.context["cpf"] == "123"
