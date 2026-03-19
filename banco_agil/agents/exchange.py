"""Agente de Cambio - cotacao de moedas."""
from banco_agil.core.agent.base import BaseAgent, Tool
from banco_agil.agents.common import make_route_tool, make_end_conversation_tool
from banco_agil.tools.exchange_api import fetch_exchange_rate as _fetch_rate

SYSTEM_PROMPT = """Voce eh o especialista em cambio do Banco Agil. Sua funcao eh consultar e informar cotacoes de moedas para o cliente.

## Servicos disponiveis:
1. Consultar cotacao de qualquer moeda em relacao ao real (BRL).

## Moedas comuns:
- USD (Dolar Americano)
- EUR (Euro)
- GBP (Libra Esterlina)
- ARS (Peso Argentino)
- BTC (Bitcoin)

## Fluxo:
1. Perguntar qual moeda o cliente deseja consultar (se nao informada).
2. Usar fetch_exchange_rate para buscar a cotacao.
3. Apresentar a cotacao de forma clara e amigavel.
4. Perguntar se deseja consultar outra moeda.
5. Quando o cliente terminar, encerrar com mensagem amigavel.

## Regras:
- NUNCA atue fora do escopo de cambio.
- Se o cliente pedir algo fora do escopo, use route_to_agent.
- Se a API falhar, informe o cliente de forma clara e ofereca tentar novamente.
"""


class ExchangeAgent(BaseAgent):
    """Agente de cambio: cotacao de moedas."""

    @property
    def name(self) -> str:
        return "exchange"

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    @property
    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="fetch_exchange_rate",
                description="Consulta a cotacao atual de uma moeda em relacao ao Real (BRL).",
                parameters={
                    "type": "object",
                    "properties": {
                        "from_currency": {
                            "type": "string",
                            "description": "Codigo da moeda de origem (ex: USD, EUR, GBP)",
                        },
                        "to_currency": {
                            "type": "string",
                            "description": "Codigo da moeda destino (padrao: BRL)",
                            "default": "BRL",
                        },
                    },
                    "required": ["from_currency"],
                },
                handler=self._fetch_rate,
            ),
            make_route_tool(),
            make_end_conversation_tool(),
        ]

    def _fetch_rate(self, from_currency: str, to_currency: str = "BRL") -> dict:
        """Handler da tool de cotacao."""
        try:
            rate = _fetch_rate(from_currency, to_currency)
            return {
                "from": from_currency,
                "to": to_currency,
                "rate": rate,
                "message": f"1 {from_currency} = {rate:.4f} {to_currency}",
            }
        except Exception as e:
            return {"error": f"Nao foi possivel consultar a cotacao: {str(e)}"}
