"""Servico de credito."""
from banco_agil.models.cliente import Cliente
from banco_agil.models.solicitacao import Solicitacao
from banco_agil.tools.csv_ops import read_csv, append_csv_row


class CreditService:
    def __init__(self, score_limite_path: str, solicitacoes_path: str):
        raw = read_csv(score_limite_path)
        self._faixas = [
            {
                "score_minimo": int(r["score_minimo"]),
                "score_maximo": int(r["score_maximo"]),
                "limite_maximo": float(r["limite_maximo"]),
            }
            for r in raw
        ]
        self.solicitacoes_path = solicitacoes_path

    def get_credit_limit(self, cliente: Cliente) -> float:
        """Retorna o limite de credito atual do cliente."""
        return cliente.limite_credito

    def request_increase(self, cliente: Cliente, novo_limite: float) -> Solicitacao:
        """Processa solicitacao de aumento de limite."""
        if novo_limite <= 0:
            raise ValueError("Novo limite deve ser positivo")

        limite_permitido = self._get_max_limit_for_score(cliente.score_credito)
        status = "aprovado" if novo_limite <= limite_permitido else "rejeitado"

        solicitacao = Solicitacao(
            cpf_cliente=cliente.cpf,
            limite_atual=cliente.limite_credito,
            novo_limite_solicitado=novo_limite,
            status_pedido=status,
        )

        append_csv_row(self.solicitacoes_path, {
            "cpf_cliente": solicitacao.cpf_cliente,
            "data_hora_solicitacao": solicitacao.data_hora_solicitacao,
            "limite_atual": solicitacao.limite_atual,
            "novo_limite_solicitado": solicitacao.novo_limite_solicitado,
            "status_pedido": solicitacao.status_pedido,
        })

        return solicitacao

    def _get_max_limit_for_score(self, score: int) -> float:
        """Retorna o limite maximo permitido para um dado score."""
        for faixa in self._faixas:
            if faixa["score_minimo"] <= score <= faixa["score_maximo"]:
                return faixa["limite_maximo"]
        return 0.0
