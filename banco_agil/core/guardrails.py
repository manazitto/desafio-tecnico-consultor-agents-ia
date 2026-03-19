"""Guardrails para validacao de escopo e sanitizacao de input."""
import re
from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage

INTENT_KEYWORDS = {
    "consulta_limite": ["limite", "credito", "quanto tenho"],
    "aumento_limite": ["aumentar", "aumento", "subir limite", "novo limite"],
    "cotacao": ["cotacao", "dolar", "euro", "cambio", "moeda"],
    "entrevista": ["entrevista", "score", "recalcular"],
    "encerrar": ["encerrar", "sair", "tchau", "fim"],
}

INJECTION_PATTERNS = [
    r"(?i)ignor[ae]\s+(todas?\s+)?(as\s+)?instru[cç][oõ]es",
    r"(?i)esquec[ae]\s+(tudo|suas?\s+regras)",
    r"(?i)voc[eê]\s+agora\s+[eé]",
    r"(?i)system\s*prompt",
    r"(?i)override",
]


@dataclass
class ScopeResult:
    in_scope: bool
    reason: str = ""


class GuardrailValidator:
    def validate_scope(self, user_input: str, allowed_intents: list[str]) -> ScopeResult:
        """Verifica se o input do usuario esta dentro do escopo permitido."""
        input_lower = user_input.lower()
        for intent in allowed_intents:
            keywords = INTENT_KEYWORDS.get(intent, [])
            if any(kw in input_lower for kw in keywords):
                return ScopeResult(in_scope=True)
        return ScopeResult(in_scope=False, reason="Solicitacao fora do escopo do agente")

    def sanitize_input(self, user_input: str) -> str:
        """Sanitiza input removendo tentativas de injection."""
        sanitized = user_input
        for pattern in INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[BLOQUEADO]", sanitized)
        return sanitized


def detect_injection(text: str) -> bool:
    """Checa se o texto contem padroes de injection."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def input_guardrail_node(state: dict) -> dict:
    """Node LangGraph de guardrail: bloqueia injection antes do agente."""
    messages = state.get("messages", [])
    if not messages:
        return {}
    last_msg = messages[-1]
    if isinstance(last_msg, HumanMessage) and detect_injection(last_msg.content):
        refusal = "Desculpe, nao posso atender a essa solicitacao. Como posso ajuda-lo com os servicos do Banco Agil?"
        return {"messages": [AIMessage(content=refusal)]}
    return {}
