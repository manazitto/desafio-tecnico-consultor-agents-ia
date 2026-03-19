"""Modelo Cliente do Banco Agil."""
import re
from dataclasses import dataclass


@dataclass
class Cliente:
    cpf: str
    nome: str
    data_nascimento: str
    score_credito: int
    limite_credito: float

    def __post_init__(self):
        self.cpf = re.sub(r"\D", "", self.cpf)

    @classmethod
    def from_csv_row(cls, row: dict) -> "Cliente":
        """Cria Cliente a partir de um dict (row de CSV)."""
        return cls(
            cpf=row["cpf"],
            nome=row["nome"],
            data_nascimento=row["data_nascimento"],
            score_credito=int(row["score_credito"]),
            limite_credito=float(row["limite_credito"]),
        )
