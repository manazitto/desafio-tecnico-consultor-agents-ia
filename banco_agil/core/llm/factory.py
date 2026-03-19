"""Factory para criacao de LLM Providers."""
from banco_agil.core.llm.base import LLMProvider


_PROVIDERS = {}


def _register_defaults():
    from banco_agil.core.llm.gemini import GeminiProvider
    _PROVIDERS["gemini"] = GeminiProvider


_register_defaults()


def create_llm_provider(provider_name: str, api_key: str, model: str) -> LLMProvider:
    """Cria o LLM provider correto baseado na config."""
    provider_cls = _PROVIDERS.get(provider_name)
    if not provider_cls:
        raise ValueError(f"Provider desconhecido: {provider_name}. Disponiveis: {list(_PROVIDERS.keys())}")
    return provider_cls(api_key=api_key, model=model)
