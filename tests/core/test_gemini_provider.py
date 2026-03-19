"""Testes para o GeminiProvider.

Requirements: LLM-02
"""
import pytest

from banco_agil.core.llm.base import LLMProvider
from banco_agil.core.llm.gemini import GeminiProvider


class TestGeminiProvider:
    """LLM-02: Implementacao concreta GeminiProvider."""

    def test_gemini_is_llm_provider(self):
        provider = GeminiProvider(api_key="fake-key", model="gemini-3-flash-preview")
        assert isinstance(provider, LLMProvider)

    def test_gemini_stores_config(self):
        provider = GeminiProvider(api_key="fake-key", model="gemini-3-flash-preview")
        assert provider._model == "gemini-3-flash-preview"

    def test_gemini_builds_tool_declarations(self):
        """Provider deve converter tool schemas para o formato Gemini."""
        provider = GeminiProvider(api_key="fake-key", model="gemini-3-flash-preview")
        tools = [
            {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {
                    "type": "object",
                    "properties": {"x": {"type": "string", "description": "param x"}},
                    "required": ["x"],
                },
            }
        ]
        declarations = provider.build_tool_declarations(tools)
        assert len(declarations) == 1
        assert declarations[0]["name"] == "test_tool"
