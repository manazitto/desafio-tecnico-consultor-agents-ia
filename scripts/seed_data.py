"""Script de geracao de dados fake para o Banco Agil."""
import csv
import os
import random

from faker import Faker

fake = Faker("pt_BR")

SCORE_LIMITE_FAIXAS = [
    {"score_minimo": "0", "score_maximo": "299", "limite_maximo": "1000.00"},
    {"score_minimo": "300", "score_maximo": "499", "limite_maximo": "5000.00"},
    {"score_minimo": "500", "score_maximo": "699", "limite_maximo": "15000.00"},
    {"score_minimo": "700", "score_maximo": "849", "limite_maximo": "30000.00"},
    {"score_minimo": "850", "score_maximo": "1000", "limite_maximo": "50000.00"},
]

SOLICITACOES_HEADERS = [
    "cpf_cliente",
    "data_hora_solicitacao",
    "limite_atual",
    "novo_limite_solicitado",
    "status_pedido",
]


def _score_to_limite(score: int) -> float:
    """Retorna o limite maximo para um dado score."""
    for faixa in SCORE_LIMITE_FAIXAS:
        if int(faixa["score_minimo"]) <= score <= int(faixa["score_maximo"]):
            return float(faixa["limite_maximo"])
    return 1000.00


def generate_clientes(output_dir: str, seed: int = 42, count: int = 50) -> None:
    """Gera clientes.csv com dados fake."""
    Faker.seed(seed)
    random.seed(seed)

    path = os.path.join(output_dir, "clientes.csv")
    fieldnames = ["cpf", "nome", "data_nascimento", "score_credito", "limite_credito"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for _ in range(count):
            score = random.randint(0, 1000)
            limite = _score_to_limite(score)
            writer.writerow({
                "cpf": fake.cpf().replace(".", "").replace("-", ""),
                "nome": fake.name(),
                "data_nascimento": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d/%m/%Y"),
                "score_credito": str(score),
                "limite_credito": f"{limite:.2f}",
            })


def generate_score_limite(output_dir: str) -> None:
    """Gera score_limite.csv com faixas de score -> limite."""
    path = os.path.join(output_dir, "score_limite.csv")
    fieldnames = ["score_minimo", "score_maximo", "limite_maximo"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(SCORE_LIMITE_FAIXAS)


def seed_all(output_dir: str, seed: int = 42) -> None:
    """Gera todos os CSVs necessarios."""
    generate_clientes(output_dir, seed=seed)
    generate_score_limite(output_dir)

    # Cria solicitacoes vazio (apenas headers)
    path = os.path.join(output_dir, "solicitacoes_aumento_limite.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SOLICITACOES_HEADERS)
        writer.writeheader()
