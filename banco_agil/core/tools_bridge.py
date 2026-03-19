"""Ponte entre servicos existentes e LangChain @tool."""
from langchain_core.tools import tool

from banco_agil.services.auth import AuthService
from banco_agil.services.credit import CreditService
from banco_agil.services.score import ScoreService
from banco_agil.tools.exchange_api import fetch_exchange_rate as _fetch_rate


def create_auth_tools(auth_service: AuthService) -> list:
    """Cria tools de autenticacao."""

    @tool
    def authenticate_client(cpf: str, data_nascimento: str) -> dict:
        """Autentica o cliente usando CPF (11 digitos) e data de nascimento (DD/MM/YYYY)."""
        result = auth_service.authenticate(cpf, data_nascimento)
        if result.locked:
            return {"authenticated": False, "locked": True, "message": "Numero maximo de tentativas excedido"}
        if result.success:
            return {
                "authenticated": True,
                "cliente": {
                    "nome": result.cliente.nome,
                    "cpf": result.cliente.cpf,
                    "score": result.cliente.score_credito,
                    "limite": result.cliente.limite_credito,
                },
            }
        return {"authenticated": False, "locked": False, "message": "CPF ou data de nascimento invalidos"}

    return [authenticate_client]


def create_credit_tools(credit_service: CreditService) -> list:
    """Cria tools de credito. Cliente vem do state via closure."""

    @tool
    def query_credit_limit(cpf: str, nome: str, score: int, limite: float) -> dict:
        """Consulta o limite de credito atual do cliente. Passe os dados do cliente autenticado."""
        return {"limite_atual": limite, "nome_cliente": nome}

    @tool
    def request_credit_increase(cpf: str, nome: str, score: int, limite_atual: float, novo_limite: float) -> dict:
        """Solicita aumento de limite de credito. Passe dados do cliente e o novo limite desejado."""
        from banco_agil.models.cliente import Cliente
        cliente = Cliente(cpf=cpf, nome=nome, data_nascimento="", score_credito=score, limite_credito=limite_atual)
        try:
            result = credit_service.request_increase(cliente, novo_limite)
            return {
                "status": result.status_pedido,
                "limite_atual": result.limite_atual,
                "novo_limite_solicitado": result.novo_limite_solicitado,
            }
        except ValueError as e:
            return {"error": str(e)}

    return [query_credit_limit, request_credit_increase]


def create_interview_tools(score_service: ScoreService, csv_path: str) -> list:
    """Cria tools de entrevista de credito."""

    @tool
    def calculate_new_score(
        cpf: str,
        renda_mensal: float,
        tipo_emprego: str,
        despesas_fixas: float,
        num_dependentes: int,
        tem_dividas: bool,
    ) -> dict:
        """Calcula novo score de credito com dados da entrevista. Passe o CPF do cliente."""
        new_score = score_service.calculate(
            renda_mensal=renda_mensal,
            tipo_emprego=tipo_emprego,
            despesas_fixas=despesas_fixas,
            num_dependentes=num_dependentes,
            tem_dividas=tem_dividas,
        )
        if csv_path:
            score_service.update_score(csv_path, cpf, new_score)
        return {"novo_score": new_score, "mensagem": f"Score atualizado para {new_score}"}

    return [calculate_new_score]


def create_exchange_tools() -> list:
    """Cria tools de cambio."""

    @tool
    def fetch_exchange_rate(from_currency: str, to_currency: str = "BRL") -> dict:
        """Consulta a cotacao atual de uma moeda em relacao ao Real (BRL)."""
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

    return [fetch_exchange_rate]


def create_routing_tools() -> list:
    """Cria tool de roteamento entre agentes."""

    @tool
    def route_to_agent(target_agent: str, reason: str = "") -> dict:
        """Redireciona para outro agente bancario. SOMENTE use para servicos bancarios (credit, exchange, credit_interview, triage). NAO use para pedidos fora do escopo — responda com texto de recusa."""
        return {"action": "route", "target_agent": target_agent, "reason": reason}

    return [route_to_agent]


def create_end_tools() -> list:
    """Cria tool de encerramento de conversa."""

    @tool
    def end_conversation(farewell_message: str) -> dict:
        """Encerra o atendimento com mensagem de despedida."""
        return {"action": "end", "message": farewell_message}

    return [end_conversation]
