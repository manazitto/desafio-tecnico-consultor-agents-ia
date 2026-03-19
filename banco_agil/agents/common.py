"""Tools comuns compartilhadas entre agentes."""
from banco_agil.core.agent.base import Tool, HandoffSignal


def make_route_tool() -> Tool:
    """Cria tool de roteamento para outro agente."""
    return Tool(
        name="route_to_agent",
        description="Redireciona o cliente para outro agente especializado. Use 'credit' para credito, 'exchange' para cambio, 'credit_interview' para entrevista de credito, 'triage' para voltar ao inicio.",
        parameters={
            "type": "object",
            "properties": {
                "target_agent": {
                    "type": "string",
                    "description": "Nome do agente destino: credit, exchange, credit_interview, triage",
                    "enum": ["credit", "exchange", "credit_interview", "triage"],
                },
                "reason": {
                    "type": "string",
                    "description": "Motivo do redirecionamento",
                },
            },
            "required": ["target_agent"],
        },
        handler=lambda target_agent, reason="": HandoffSignal(
            target_agent=target_agent, context={"reason": reason}
        ),
    )


def make_end_conversation_tool() -> Tool:
    """Cria tool de encerramento de conversa."""
    return Tool(
        name="end_conversation",
        description="Encerra o atendimento quando o cliente deseja finalizar a conversa.",
        parameters={
            "type": "object",
            "properties": {
                "farewell_message": {
                    "type": "string",
                    "description": "Mensagem de despedida para o cliente",
                },
            },
            "required": ["farewell_message"],
        },
        handler=lambda farewell_message: {"action": "end", "message": farewell_message},
    )
