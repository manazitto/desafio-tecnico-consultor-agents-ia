"""Servico de autenticacao de clientes."""
import re
from dataclasses import dataclass
from typing import Optional

from banco_agil.models.cliente import Cliente
from banco_agil.tools.csv_ops import read_csv


@dataclass
class AuthResult:
    success: bool
    cliente: Optional[Cliente] = None
    locked: bool = False


class AuthService:
    MAX_ATTEMPTS = 3

    def __init__(self, csv_path: str):
        raw_data = read_csv(csv_path)
        self._clientes = {row["cpf"]: row for row in raw_data}
        self._failed_attempts = 0

    def authenticate(self, cpf: str, data_nascimento: str) -> AuthResult:
        """Autentica cliente por CPF e data de nascimento."""
        if self._failed_attempts >= self.MAX_ATTEMPTS:
            return AuthResult(success=False, locked=True)

        cpf_clean = re.sub(r"\D", "", cpf)
        row = self._clientes.get(cpf_clean)

        if row and row["data_nascimento"] == data_nascimento:
            self._failed_attempts = 0
            return AuthResult(success=True, cliente=Cliente.from_csv_row(row))

        self._failed_attempts += 1
        if self._failed_attempts >= self.MAX_ATTEMPTS:
            return AuthResult(success=False, locked=True)
        return AuthResult(success=False)
