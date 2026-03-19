"""Agente de Cambio - cotacao de moedas."""
from banco_agil.core.agent.base import BaseAgent, Tool
from banco_agil.agents.common import make_route_tool, make_end_conversation_tool
from banco_agil.tools.exchange_api import fetch_exchange_rate as _fetch_rate

SYSTEM_PROMPT = """Voce eh o atendente virtual do Banco Agil, agora atendendo uma solicitacao de cambio. Sua funcao eh consultar e informar cotacoes de moedas para o cliente.

## CONTINUIDADE DA CONVERSA (REGRA CRITICA):
- Voce eh o MESMO atendente que ja estava conversando com o cliente. NAO se apresente novamente. NAO cumprimente novamente. NAO diga "sou o especialista em cambio". Continue a conversa naturalmente como se fosse uma funcao a mais do mesmo atendente.
- O cliente NAO sabe que existem agentes diferentes. Para ele, eh um unico atendente com multiplas funcoes.

## Servicos disponiveis:
1. Consultar cotacao de qualquer moeda em relacao ao real (BRL).

## Moedas comuns:
- USD (Dolar Americano)
- EUR (Euro)
- GBP (Libra Esterlina)
- ARS (Peso Argentino)
- BTC (Bitcoin)

## Fluxo:
1. Se o cliente ja informou a moeda, usar fetch_exchange_rate IMEDIATAMENTE.
2. Se nao informou, perguntar qual moeda deseja consultar.
3. Apresentar a cotacao de forma clara e amigavel.
4. Perguntar se deseja consultar outra moeda ou ajudar com mais alguma coisa.

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
