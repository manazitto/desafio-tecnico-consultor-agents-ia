"""Client para API de cambio."""
import httpx


def fetch_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Consulta cotacao de moeda via AwesomeAPI."""
    pair = f"{from_currency}{to_currency}"
    response = httpx.get(f"https://economia.awesomeapi.com.br/json/last/{from_currency}-{to_currency}")
    response.raise_for_status()
    data = response.json()
    return float(data[pair]["bid"])
