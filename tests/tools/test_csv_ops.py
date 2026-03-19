"""Testes para operacoes de CSV.

Requirements: DATA-01, GUARD-03
"""
import pytest

from banco_agil.tools.csv_ops import read_csv, append_csv_row, update_csv_row


@pytest.fixture
def sample_csv(tmp_path):
    """Cria um CSV de teste."""
    csv_path = str(tmp_path / "test.csv")
    with open(csv_path, "w") as f:
        f.write("cpf,nome,score\n")
        f.write("12345678900,Maria,720\n")
        f.write("98765432100,Joao,450\n")
    return csv_path


class TestReadCsv:
    """Leitura de CSV."""

    def test_read_csv_returns_list_of_dicts(self, sample_csv):
        """read_csv retorna lista de dicionarios com headers como chaves."""
        result = read_csv(sample_csv)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["cpf"] == "12345678900"
        assert result[0]["nome"] == "Maria"

    def test_read_csv_missing_file_raises_error(self):
        """Arquivo inexistente deve levantar FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_csv("/caminho/que/nao/existe.csv")


class TestWriteCsv:
    """Escrita em CSV."""

    def test_write_csv_appends_row(self, sample_csv):
        """append_csv_row adiciona uma linha ao CSV existente."""
        new_row = {"cpf": "11122233344", "nome": "Ana", "score": "600"}
        append_csv_row(sample_csv, new_row)
        result = read_csv(sample_csv)
        assert len(result) == 3
        assert result[2]["nome"] == "Ana"


class TestUpdateCsv:
    """Atualizacao de CSV."""

    def test_update_csv_row_by_key(self, sample_csv):
        """update_csv_row atualiza uma linha especifica por chave."""
        update_csv_row(sample_csv, key_column="cpf", key_value="12345678900", updates={"score": "800"})
        result = read_csv(sample_csv)
        row = next(r for r in result if r["cpf"] == "12345678900")
        assert row["score"] == "800"
