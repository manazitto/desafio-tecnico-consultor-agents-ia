"""Testes para a abstracao de LLM Provider.

Requirements: LLM-01, LLM-03
"""
import pytest
from abc import ABC

from banco_agil.core.llm.base import LLMProvider
from banco_agil.core.llm.factory import create_llm_provider


class TestLLMProviderInterface:
    """LLM-01: Interface abstrata LLMProvider."""

    def test_llm_provider_interface_has_required_methods(self):
        """LLMProvider deve definir chat() e chat_with_tools() como metodos abstratos."""
        assert hasattr(LLMProvider, "chat")
        assert hasattr(LLMProvider, "chat_with_tools")
        assert issubclass(LLMProvider, ABC)

        with pytest.raises(TypeError):
            LLMProvider()


class TestLLMFactory:
    """LLM-03: Factory cria provider a partir de config."""

    def test_factory_creates_provider_from_config(self):
        """Factory deve criar o provider correto baseado em string de config."""
        provider = create_llm_provider(provider_name="gemini", api_key="fake-key", model="gemini-3-flash-preview")
        assert isinstance(provider, LLMProvider)
