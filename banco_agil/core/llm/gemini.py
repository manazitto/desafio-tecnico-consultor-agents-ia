"""Gemini LLM Provider com tracing LangSmith."""
from google import genai
from google.genai import types

from banco_agil.core.llm.base import LLMProvider

try:
    from langsmith import traceable
    from langsmith.run_helpers import get_current_run_tree
    _HAS_LANGSMITH = True
except ImportError:
    _HAS_LANGSMITH = False

    def traceable(*args, **kwargs):
        """Fallback no-op decorator quando LangSmith nao esta instalado."""
        def decorator(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return decorator


class GeminiProvider(LLMProvider):
    """Provider para Google Gemini API com tracing opcional via LangSmith."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self._api_key = api_key
        self._model = model
        self._client = genai.Client(api_key=api_key)

    @traceable(run_type="llm", name="gemini_chat")
    def chat(self, messages: list[dict]) -> str:
        """Envia mensagens e retorna resposta de texto."""
        contents = self._build_contents(messages)
        system_instruction = self.get_system_instruction(messages)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
        ) if system_instruction else None

        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=config,
        )
        return response.text

    @traceable(run_type="llm", name="gemini_chat_with_tools")
    def chat_with_tools(self, messages: list[dict], tools: list[dict]) -> dict:
        """Envia mensagens com tools e retorna resposta (texto ou tool call)."""
        contents = self._build_contents(messages)
        declarations = self.build_tool_declarations(tools)
        system_instruction = self.get_system_instruction(messages)

        gemini_tools = [types.Tool(function_declarations=declarations)]

        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=gemini_tools,
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode="AUTO")
                ),
            ),
        )

        candidate = response.candidates[0]
        part = candidate.content.parts[0]

        if part.function_call:
            return {
                "type": "tool_call",
                "tool_name": part.function_call.name,
                "arguments": dict(part.function_call.args) if part.function_call.args else {},
            }

        return {
            "type": "text",
            "content": part.text,
        }

    def build_tool_declarations(self, tools: list[dict]) -> list[dict]:
        """Converte tool schemas para formato Gemini function declarations."""
        declarations = []
        for tool in tools:
            decl = {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            }
            declarations.append(decl)
        return declarations

    def _build_contents(self, messages: list[dict]) -> list:
        """Converte mensagens no formato padrao para formato Gemini."""
        contents = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                continue
            gemini_role = "user" if role == "user" else "model"
            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=msg["content"])],
                )
            )
        return contents

    def get_system_instruction(self, messages: list[dict]) -> str | None:
        """Extrai system instruction das mensagens."""
        for msg in messages:
            if msg["role"] == "system":
                return msg["content"]
        return None
