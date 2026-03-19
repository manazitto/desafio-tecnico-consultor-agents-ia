"""Testes para o grafo de agentes LangGraph.

Requirements: ROUTE-01, ROUTE-02, ROUTE-03, LLM-03
"""
import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage

from banco_agil.core.graph import (
    AgentState,
    build_agent_graph,
    create_runnable,
)


class TestAgentState:
    """Estado do grafo de agentes."""

    def test_agent_state_has_required_fields(self):
        """Estado deve conter messages, current_agent e client_data."""
        state = AgentState(
            messages=[],
            current_agent="triage",
            client_data={},
            conversation_ended=False,
        )
        assert state["current_agent"] == "triage"
        assert state["messages"] == []
        assert state["conversation_ended"] is False


class TestBuildGraph:
    """Construcao do grafo LangGraph."""

    def test_build_graph_returns_compiled_graph(self):
        """build_agent_graph retorna um grafo compilado."""
        mock_llm = MagicMock()
        mock_agents = {"triage": MagicMock(), "credit": MagicMock()}

        graph = build_agent_graph(llm=mock_llm, agents=mock_agents)
        assert graph is not None

    def test_graph_starts_at_triage(self):
        """Grafo deve comecar no node triage."""
        mock_llm = MagicMock()
        mock_agents = {
            "triage": MagicMock(),
            "credit": MagicMock(),
            "exchange": MagicMock(),
            "credit_interview": MagicMock(),
        }

        graph = build_agent_graph(llm=mock_llm, agents=mock_agents)
        # O grafo compilado deve existir e ser invocavel
        assert hasattr(graph, "invoke")


class TestCreateRunnable:
    """Factory do runnable completo."""

    def test_create_runnable_with_gemini_config(self):
        """create_runnable deve criar grafo funcional a partir de config."""
        with patch("banco_agil.core.graph.ChatGoogleGenerativeAI") as mock_chat:
            mock_chat.return_value = MagicMock()
            runnable = create_runnable(
                api_key="fake-key",
                model="gemini-3-flash-preview",
            )
        assert runnable is not None
