"""Testes para o servico de autenticacao.

Requirements: AUTH-03, AUTH-04, AUTH-05
"""
import pytest
from unittest.mock import patch

from banco_agil.services.auth import AuthService


@pytest.fixture
def clientes_data():
    """Base de clientes fake para testes (datas em formato BR)."""
    return [
        {
            "cpf": "12345678900",
            "nome": "Maria Silva",
            "data_nascimento": "15/05/1990",
            "score_credito": "720",
            "limite_credito": "15000.00",
        },
        {
            "cpf": "98765432100",
            "nome": "Joao Santos",
            "data_nascimento": "20/11/1985",
            "score_credito": "450",
            "limite_credito": "5000.00",
        },
    ]


@pytest.fixture
def auth_service(clientes_data):
    """AuthService com dados mockados."""
    with patch("banco_agil.services.auth.read_csv", return_value=clientes_data):
        service = AuthService(csv_path="fake_path.csv")
    return service


class TestAuthentication:
    """AUTH-03: Validacao de CPF + data de nascimento contra clientes.csv."""

    def test_authenticate_valid_cpf_and_dob(self, auth_service):
        """Autenticacao bem-sucedida com CPF e data no formato BR (DD/MM/YYYY)."""
        result = auth_service.authenticate("12345678900", "15/05/1990")
        assert result.success is True
        assert result.cliente.nome == "Maria Silva"

    def test_authenticate_invalid_cpf(self, auth_service):
        """Autenticacao falha com CPF inexistente."""
        result = auth_service.authenticate("00000000000", "15/05/1990")
        assert result.success is False
        assert result.cliente is None

    def test_authenticate_wrong_dob(self, auth_service):
        """Autenticacao falha com CPF correto mas data errada."""
        result = auth_service.authenticate("12345678900", "01/01/2000")
        assert result.success is False
        assert result.cliente is None

    def test_authenticate_cpf_with_punctuation(self, auth_service):
        """CPF com pontuacao deve ser normalizado e aceito."""
        result = auth_service.authenticate("123.456.789-00", "15/05/1990")
        assert result.success is True
        assert result.cliente.nome == "Maria Silva"


class TestAuthAttempts:
    """AUTH-04/AUTH-05: Controle de tentativas de autenticacao."""

    def test_authenticate_allows_3_attempts(self, auth_service):
        """Sistema permite ate 3 tentativas de autenticacao."""
        auth_service.authenticate("00000000000", "01/01/2000")
        auth_service.authenticate("00000000000", "01/01/2000")
        result = auth_service.authenticate("12345678900", "15/05/1990")
        assert result.success is True

    def test_authenticate_locks_after_3_failures(self, auth_service):
        """Apos 3 falhas consecutivas, autenticacao eh bloqueada."""
        auth_service.authenticate("00000000000", "01/01/2000")
        auth_service.authenticate("00000000000", "01/01/2000")
        auth_service.authenticate("00000000000", "01/01/2000")
        result = auth_service.authenticate("12345678900", "15/05/1990")
        assert result.success is False
        assert result.locked is True
