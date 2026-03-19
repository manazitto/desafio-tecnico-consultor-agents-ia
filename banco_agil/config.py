"""Configuracao do sistema Banco Agil."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")

CLIENTES_CSV = str(DATA_DIR / "clientes.csv")
SCORE_LIMITE_CSV = str(DATA_DIR / "score_limite.csv")
SOLICITACOES_CSV = str(DATA_DIR / "solicitacoes_aumento_limite.csv")

# LangSmith
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "case-banco-agil")
LANGSMITH_TRACING = bool(LANGSMITH_API_KEY)
