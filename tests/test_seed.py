"""Testes para o script de seed de dados.

Requirements: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05
"""
import csv
import os
import pytest

from scripts.seed_data import generate_clientes, generate_score_limite, seed_all


@pytest.fixture
def seed_dir(tmp_path):
    """Diretorio temporario para gerar os CSVs."""
    return str(tmp_path)


class TestSeedClientes:
    """DATA-01/02: Geracao de clientes fake."""

    def test_seed_generates_clientes_csv(self, seed_dir):
        """Script gera arquivo clientes.csv."""
        generate_clientes(output_dir=seed_dir)
        assert os.path.exists(os.path.join(seed_dir, "clientes.csv"))

    def test_seed_generates_at_least_50_clients(self, seed_dir):
        """clientes.csv deve ter pelo menos 50 registros."""
        generate_clientes(output_dir=seed_dir)
        with open(os.path.join(seed_dir, "clientes.csv")) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 50


class TestSeedScoreLimite:
    """DATA-03: Tabela de faixas score -> limite."""

    def test_seed_generates_score_limite_csv(self, seed_dir):
        """Script gera arquivo score_limite.csv."""
        generate_score_limite(output_dir=seed_dir)
        path = os.path.join(seed_dir, "score_limite.csv")
        assert os.path.exists(path)
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 3
        assert "score_minimo" in rows[0]
        assert "score_maximo" in rows[0]
        assert "limite_maximo" in rows[0]


class TestSeedReproducibility:
    """DATA-04: Reproducibilidade do seed."""

    def test_seed_is_reproducible(self, tmp_path):
        """Duas execucoes com mesma seed geram dados identicos."""
        dir1 = str(tmp_path / "run1")
        dir2 = str(tmp_path / "run2")
        os.makedirs(dir1)
        os.makedirs(dir2)

        generate_clientes(output_dir=dir1, seed=42)
        generate_clientes(output_dir=dir2, seed=42)

        with open(os.path.join(dir1, "clientes.csv")) as f1, \
             open(os.path.join(dir2, "clientes.csv")) as f2:
            assert f1.read() == f2.read()


class TestSeedSolicitacoes:
    """DATA-05: CSV de solicitacoes vazio."""

    def test_seed_creates_empty_solicitacoes_csv(self, seed_dir):
        """seed_all cria solicitacoes_aumento_limite.csv com headers apenas."""
        seed_all(output_dir=seed_dir)
        path = os.path.join(seed_dir, "solicitacoes_aumento_limite.csv")
        assert os.path.exists(path)
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 0
        with open(path) as f:
            header = f.readline().strip()
        assert "cpf_cliente" in header
        assert "status_pedido" in header
