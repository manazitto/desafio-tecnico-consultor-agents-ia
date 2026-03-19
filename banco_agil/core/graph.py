"""Grafo de agentes LangGraph para o Banco Agil."""
import re
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from banco_agil.config import CLIENTES_CSV, SCORE_LIMITE_CSV, SOLICITACOES_CSV
from banco_agil.core.guardrails import INJECTION_PATTERNS
from banco_agil.core.prompts import build_system_prompt
from banco_agil.core.tools_bridge import (
    create_auth_tools,
    create_credit_tools,
    create_end_tools,
    create_exchange_tools,
    create_interview_tools,
    create_routing_tools,
)
from banco_agil.services.auth import AuthService
from banco_agil.services.credit import CreditService
from banco_agil.services.score import ScoreService


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str
    client_data: dict
    conversation_ended: bool


REFUSAL_MSG = "Desculpe, nao posso atender a essa solicitacao. Como posso ajuda-lo com os servicos do Banco Agil?"


def _check_injection(text: str) -> bool:
    """Checa padroes de injection deterministicamente."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def input_guardrail_node(state: AgentState) -> dict:
    """Node de guardrail: bloqueia injection antes do agente."""
    last_msg = state["messages"][-1]
    if isinstance(last_msg, HumanMessage) and _check_injection(last_msg.content):
        return {"messages": [AIMessage(content=REFUSAL_MSG)]}
    return {}


def _make_agent_node(agent_name: str, llm_with_tools):
    """Factory de nodes de agente."""

    def agent_node(state: AgentState) -> dict:
        prompt = build_system_prompt(agent_name, state["client_data"])
        messages = [SystemMessage(content=prompt)] + list(state["messages"])
        response = llm_with_tools.invoke(messages)
        return {"messages": [response], "current_agent": agent_name}

    return agent_node


def _make_end_node():
    def end_node(state: AgentState) -> dict:
        return {"conversation_ended": True}

    return end_node


def _route_after_guardrail(state: AgentState) -> str:
    """Rota apos guardrail: se a ultima msg eh AIMessage (recusa), vai pro END."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage):
        return END
    return state.get("current_agent", "triage")


def _route_after_agent(state: AgentState) -> str:
    """Rota apos agente: tool call ou resposta texto."""
    last = state["messages"][-1]
    if not isinstance(last, AIMessage):
        return END
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return END

    for tc in last.tool_calls:
        if tc["name"] == "route_to_agent":
            return "tools"
        if tc["name"] == "end_conversation":
            return "tools"

    return "tools"


def _route_after_tools(state: AgentState) -> str:
    """Apos tool execution, decide pra onde ir."""
    messages = state["messages"]

    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            if '"action": "route"' in msg.content or "'action': 'route'" in msg.content:
                import json
                try:
                    data = json.loads(msg.content)
                    target = data.get("target_agent")
                    if target:
                        return target
                except (json.JSONDecodeError, TypeError):
                    pass
            if '"action": "end"' in msg.content or "'action': 'end'" in msg.content:
                return "end_node"
            break

    return state.get("current_agent", "triage")


def build_agent_graph(llm, agents: dict):
    """Constroi e compila o StateGraph de agentes."""
    seen_names = set()
    all_tools = []
    for tool_list in agents.values():
        if isinstance(tool_list, list):
            for t in tool_list:
                if t.name not in seen_names:
                    seen_names.add(t.name)
                    all_tools.append(t)

    llm_with_tools = llm.bind_tools(all_tools)

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("guardrail", input_guardrail_node)
    graph.add_node("triage", _make_agent_node("triage", llm_with_tools))
    graph.add_node("credit", _make_agent_node("credit", llm_with_tools))
    graph.add_node("exchange", _make_agent_node("exchange", llm_with_tools))
    graph.add_node("credit_interview", _make_agent_node("credit_interview", llm_with_tools))
    graph.add_node("tools", ToolNode(all_tools))
    graph.add_node("end_node", _make_end_node())

    # Entry
    graph.set_entry_point("guardrail")

    # Edges from guardrail
    graph.add_conditional_edges("guardrail", _route_after_guardrail, {
        "triage": "triage",
        "credit": "credit",
        "exchange": "exchange",
        "credit_interview": "credit_interview",
        END: END,
    })

    # Edges from agent nodes
    for agent_name in ["triage", "credit", "exchange", "credit_interview"]:
        graph.add_conditional_edges(agent_name, _route_after_agent, {
            "tools": "tools",
            END: END,
        })

    # Edges from tools
    graph.add_conditional_edges("tools", _route_after_tools, {
        "triage": "triage",
        "credit": "credit",
        "exchange": "exchange",
        "credit_interview": "credit_interview",
        "end_node": "end_node",
    })

    # End node
    graph.add_edge("end_node", END)

    return graph.compile()


def create_runnable(api_key: str, model: str = "gemini-3-flash-preview"):
    """Factory: cria LLM, servicos, tools e retorna grafo compilado."""
    llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)

    auth_service = AuthService(csv_path=CLIENTES_CSV)
    credit_service = CreditService(score_limite_path=SCORE_LIMITE_CSV, solicitacoes_path=SOLICITACOES_CSV)
    score_service = ScoreService()

    agents = {
        "triage": (
            create_auth_tools(auth_service)
            + create_routing_tools()
            + create_end_tools()
        ),
        "credit": (
            create_credit_tools(credit_service)
            + create_routing_tools()
            + create_end_tools()
        ),
        "exchange": (
            create_exchange_tools()
            + create_routing_tools()
            + create_end_tools()
        ),
        "credit_interview": (
            create_interview_tools(score_service, CLIENTES_CSV)
            + create_routing_tools()
            + create_end_tools()
        ),
    }

    return build_agent_graph(llm, agents)
