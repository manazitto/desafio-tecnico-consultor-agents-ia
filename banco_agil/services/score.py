"""Servico de calculo e atualizacao de score."""
from banco_agil.tools.csv_ops import update_csv_row

PESO_RENDA = 30

PESO_EMPREGO = {
    "formal": 300,
    "autonomo": 200,
    "desempregado": 0,
}

PESO_DEPENDENTES = {
    0: 100,
    1: 80,
    2: 60,
}
PESO_DEPENDENTES_3_PLUS = 30

PESO_DIVIDAS = {
    True: -100,
    False: 100,
}


class ScoreService:
    def calculate(
        self,
        renda_mensal: float,
        tipo_emprego: str,
        despesas_fixas: float,
        num_dependentes: int,
        tem_dividas: bool,
    ) -> int:
        """Calcula score de credito com formula ponderada (0-1000)."""
        renda_component = (renda_mensal / (despesas_fixas + 1)) * PESO_RENDA
        emprego_component = PESO_EMPREGO.get(tipo_emprego, 0)
        dep_component = PESO_DEPENDENTES.get(num_dependentes, PESO_DEPENDENTES_3_PLUS)
        divida_component = PESO_DIVIDAS[tem_dividas]

        raw_score = renda_component + emprego_component + dep_component + divida_component
        return max(0, min(1000, int(raw_score)))

    def update_score(self, csv_path: str, cpf: str, new_score: int) -> None:
        """Atualiza o score de um cliente no CSV."""
        update_csv_row(csv_path, key_column="cpf", key_value=cpf, updates={"score_credito": str(new_score)})
