"""Modelo Solicitacao de aumento de limite."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Solicitacao:
    cpf_cliente: str
    limite_atual: float
    novo_limite_solicitado: float
    status_pedido: str
    data_hora_solicitacao: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def status(self) -> str:
        """Alias para status_pedido."""
        return self.status_pedido
