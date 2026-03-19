"""Agente de Entrevista de Credito - recalculo de score."""
from banco_agil.core.agent.base import BaseAgent, Tool
from banco_agil.agents.common import make_route_tool, make_end_conversation_tool
from banco_agil.services.score import ScoreService
from banco_agil.models.cliente import Cliente

SYSTEM_PROMPT = """Voce eh o atendente virtual do Banco Agil, agora conduzindo uma entrevista financeira para recalcular o score de credito do cliente.

## CONTINUIDADE DA CONVERSA (REGRA CRITICA):
- Voce eh o MESMO atendente que ja estava conversando com o cliente. NAO se apresente novamente. NAO cumprimente novamente. NAO diga "sou o analista de credito". Continue a conversa naturalmente, apenas explique que vai fazer algumas perguntas para atualizar o perfil.
- O cliente NAO sabe que existem agentes diferentes. Para ele, eh um unico atendente com multiplas funcoes.

## Perguntas obrigatorias (colete TODAS antes de calcular):
1. Qual a sua renda mensal? (valor numerico em reais)
2. Qual o tipo de emprego? (formal, autonomo ou desempregado)
3. Qual o valor das suas despesas fixas mensais? (valor numerico em reais)
4. Quantos dependentes voce tem? (numero inteiro)
5. Voce possui dividas ativas? (sim ou nao)

## Fluxo:
1. Explicar que fara algumas perguntas para atualizar o perfil de credito.
2. Fazer cada pergunta de forma natural e conversacional (uma por vez).
3. Apos coletar TODAS as respostas, usar calculate_new_score com os dados.
4. Informar o novo score ao cliente.
5. Usar route_to_agent para redirecionar ao agente de credito para nova analise.

## Regras:
- Faca as perguntas de forma empática e natural, nao como um questionário.
- Se o cliente der uma resposta ambígua, peca esclarecimento.
- NUNCA atue fora do escopo da entrevista de credito.
- Converta respostas do cliente para os tipos corretos antes de chamar a tool.
  - tipo_emprego: "formal", "autonomo" ou "desempregado"
  - tem_dividas: true ou false
"""


class CreditInterviewAgent(BaseAgent):
    """Agente de entrevista de credito: recalculo de score."""

    def __init__(self, score_service: ScoreService = None, cliente: Cliente = None, clientes_csv_path: str = None):
        self._score_service = score_service
        self._cliente = cliente
        self._clientes_csv_path = clientes_csv_path

    @property
    def name(self) -> str:
        return "credit_interview"

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    @property
    def tools(self) -> list[Tool]:
        return [
            Tool(
                name="calculate_new_score",
                description="Calcula o novo score de credito com base nos dados financeiros coletados na entrevista. Atualiza o score do cliente no sistema.",
                parameters={
                    "type": "object",
                    "properties": {
                        "renda_mensal": {
                            "type": "number",
                            "description": "Renda mensal do cliente em reais",
                        },
                        "tipo_emprego": {
                            "type": "string",
                            "description": "Tipo de emprego: formal, autonomo ou desempregado",
                            "enum": ["formal", "autonomo", "desempregado"],
                        },
                        "despesas_fixas": {
                            "type": "number",
                            "description": "Despesas fixas mensais em reais",
                        },
                        "num_dependentes": {
                            "type": "integer",
                            "description": "Numero de dependentes",
                        },
                        "tem_dividas": {
                            "type": "boolean",
                            "description": "Se o cliente possui dividas ativas",
                        },
                    },
                    "required": ["renda_mensal", "tipo_emprego", "despesas_fixas", "num_dependentes", "tem_dividas"],
                },
                handler=self._calculate_score,
            ),
            make_route_tool(),
            make_end_conversation_tool(),
        ]

    def _calculate_score(
        self,
        renda_mensal: float,
        tipo_emprego: str,
        despesas_fixas: float,
        num_dependentes: int,
        tem_dividas: bool,
    ) -> dict:
        """Handler da tool de calculo de score."""
        if not self._score_service:
            return {"error": "Servico nao configurado"}

        new_score = self._score_service.calculate(
            renda_mensal=renda_mensal,
            tipo_emprego=tipo_emprego,
            despesas_fixas=despesas_fixas,
            num_dependentes=num_dependentes,
            tem_dividas=tem_dividas,
        )

        old_score = self._cliente.score_credito if self._cliente else 0

        if self._cliente and self._clientes_csv_path:
            self._score_service.update_score(self._clientes_csv_path, self._cliente.cpf, new_score)
            self._cliente.score_credito = new_score

        return {
            "score_anterior": old_score,
            "novo_score": new_score,
            "mensagem": f"Score atualizado de {old_score} para {new_score}",
        }
