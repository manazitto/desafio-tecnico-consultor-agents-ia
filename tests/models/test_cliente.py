"""Testes para o modelo Cliente.

Requirements: AUTH-03
"""
import pytest

from banco_agil.models.cliente import Cliente


class TestCliente:
    """Modelo Cliente."""

    def test_cliente_from_csv_row(self):
        """Cliente pode ser criado a partir de um dict (row do CSV)."""
        row = {
            "cpf": "12345678900",
            "nome": "Maria Silva",
            "data_nascimento": "1990-05-15",
            "score_credito": "720",
            "limite_credito": "15000.00",
        }
        cliente = Cliente.from_csv_row(row)
        assert cliente.cpf == "12345678900"
        assert cliente.nome == "Maria Silva"
        assert cliente.score_credito == 720
        assert cliente.limite_credito == 15000.00

    def test_cliente_cpf_normalized(self):
        """CPF deve ser armazenado apenas com digitos."""
        cliente = Cliente(
            cpf="123.456.789-00",
            nome="Maria Silva",
            data_nascimento="1990-05-15",
            score_credito=720,
            limite_credito=15000.00,
        )
        assert cliente.cpf == "12345678900"
