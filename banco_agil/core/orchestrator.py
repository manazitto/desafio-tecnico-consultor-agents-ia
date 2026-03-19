"""Orquestrador de agentes - gerencia estado da conversa e handoffs."""
import json
import logging

from banco_agil.core.agent.base import BaseAgent, HandoffSignal
from banco_agil.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)

ROUTING_KEYWORDS = {
    "credit": ["limite", "credito", "aumento", "aumentar"],
    "exchange": ["cotacao", "dolar", "euro", "cambio", "moeda"],
    "credit_interview": ["entrevista", "score", "recalcular"],
}


class Orchestrator:
    """Gerencia o fluxo de conversa entre agentes de forma transparente."""

    def __init__(self, llm_provider: LLMProvider = None):
        self._agents: dict[str, BaseAgent] = {}
        self._llm = llm_provider
        self._current_agent: str | None = None
        self._conversation_history: list[dict] = []
        self._conversation_ended = False

    @property
    def current_agent_name(self) -> str | None:
        return self._current_agent

    @property
    def is_ended(self) -> bool:
        return self._conversation_ended

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """Registra um agente no orquestrador."""
        self._agents[name] = agent

    def set_active_agent(self, name: str) -> None:
        """Define o agente ativo."""
        if name not in self._agents:
            raise ValueError(f"Agente '{name}' nao registrado")
        self._current_agent = name

    def resolve_agent(self, user_input: str) -> str:
        """Resolve qual agente deve atender baseado na intencao do usuario.

        Checa agentes mais especificos primeiro para evitar falsos positivos
        (ex: 'entrevista de credito' nao deve rotear para 'credit').
        """
        input_lower = user_input.lower()

        # Ordem de prioridade: mais especifico primeiro
        priority_order = ["credit_interview", "credit", "exchange"]

        for agent_name in priority_order:
            if agent_name not in self._agents:
                continue
            keywords = ROUTING_KEYWORDS.get(agent_name, [])
            if any(kw in input_lower for kw in keywords):
                return agent_name

        return None

    async def process_message(self, user_message: str) -> str:
        """Processa mensagem do usuario e retorna resposta."""
        if self._conversation_ended:
            return "Atendimento encerrado. Obrigado por utilizar o Banco Agil!"

        if not self._current_agent:
            self._current_agent = "triage"

        agent = self._agents[self._current_agent]
        self._conversation_history.append({"role": "user", "content": user_message})

        messages = [
            {"role": "system", "content": agent.system_prompt},
            *self._conversation_history,
        ]

        tools_schemas = agent.get_tools_schemas()
        tools_map = agent.get_tools_map()

        max_tool_rounds = 5
        for _ in range(max_tool_rounds):
            response = self._llm.chat_with_tools(messages, tools_schemas)

            if response["type"] == "text":
                assistant_msg = response["content"]
                self._conversation_history.append({"role": "assistant", "content": assistant_msg})
                return assistant_msg

            if response["type"] == "tool_call":
                tool_name = response["tool_name"]
                arguments = response["arguments"]
                logger.info(f"Tool call: {tool_name}({arguments})")

                handler = tools_map.get(tool_name)
                if not handler:
                    tool_result = {"error": f"Tool '{tool_name}' nao encontrada"}
                else:
                    try:
                        tool_result = handler(**arguments)
                    except Exception as e:
                        logger.error(f"Erro na tool {tool_name}: {e}")
                        tool_result = {"error": str(e)}

                if isinstance(tool_result, HandoffSignal):
                    self._current_agent = tool_result.target_agent
                    agent = self._agents[self._current_agent]
                    messages = [
                        {"role": "system", "content": agent.system_prompt},
                        *self._conversation_history,
                    ]
                    tools_schemas = agent.get_tools_schemas()
                    tools_map = agent.get_tools_map()
                    continue

                if isinstance(tool_result, dict) and tool_result.get("action") == "end":
                    self._conversation_ended = True
                    end_msg = tool_result.get("message", "Obrigado por utilizar o Banco Agil!")
                    self._conversation_history.append({"role": "assistant", "content": end_msg})
                    return end_msg

                messages.append({
                    "role": "assistant",
                    "content": f"[Tool call: {tool_name}({json.dumps(arguments, ensure_ascii=False)})]",
                })
                messages.append({
                    "role": "user",
                    "content": f"[Tool result: {json.dumps(tool_result, ensure_ascii=False, default=str)}]",
                })

        return "Desculpe, tive um problema ao processar sua solicitacao. Pode tentar novamente?"
