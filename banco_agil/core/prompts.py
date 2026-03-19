"""Templates dinamicos de prompts para agentes LangGraph."""
from banco_agil.agents.triage import SYSTEM_PROMPT as TRIAGE_PROMPT
from banco_agil.agents.credit import SYSTEM_PROMPT as CREDIT_PROMPT
from banco_agil.agents.exchange import SYSTEM_PROMPT as EXCHANGE_PROMPT
from banco_agil.agents.credit_interview import SYSTEM_PROMPT as INTERVIEW_PROMPT

AGENT_PROMPTS = {
    "triage": TRIAGE_PROMPT,
    "credit": CREDIT_PROMPT,
    "exchange": EXCHANGE_PROMPT,
    "credit_interview": INTERVIEW_PROMPT,
}


def build_system_prompt(agent_name: str, client_data: dict) -> str:
    """Constroi prompt com dados do cliente injetados dinamicamente."""
    base = AGENT_PROMPTS[agent_name]
    if client_data.get("nome"):
        base += f"\n\nCliente autenticado: {client_data['nome']} (CPF: {client_data['cpf']})"
        if client_data.get("score"):
            base += f"\nScore: {client_data['score']}, Limite atual: R${client_data['limite']}"
    return base
