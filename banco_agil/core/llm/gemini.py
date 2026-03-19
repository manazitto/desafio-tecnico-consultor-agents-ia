"""Gemini LLM Provider usando langchain-google-genai."""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool as lc_tool
from langchain_google_genai import ChatGoogleGenerativeAI

from banco_agil.core.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    """Provider para Google Gemini via langchain-google-genai."""

    def __init__(self, api_key: str, model: str = "gemini-3-flash-preview"):
        self._api_key = api_key
        self._model = model
        self._llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)

    def chat(self, messages: list[dict]) -> str:
        """Envia mensagens e retorna resposta de texto."""
        lc_messages = self._to_langchain_messages(messages)
        response = self._llm.invoke(lc_messages)
        return response.content

    def chat_with_tools(self, messages: list[dict], tools: list[dict]) -> dict:
        """Envia mensagens com tools e retorna resposta (texto ou tool call)."""
        lc_tools = self._schemas_to_lc_tools(tools)
        llm_with_tools = self._llm.bind_tools(lc_tools)

        lc_messages = self._to_langchain_messages(messages)
        response = llm_with_tools.invoke(lc_messages)

        if response.tool_calls:
            tc = response.tool_calls[0]
            return {
                "type": "tool_call",
                "tool_name": tc["name"],
                "arguments": tc["args"],
            }

        return {
            "type": "text",
            "content": response.content,
        }

    def build_tool_declarations(self, tools: list[dict]) -> list[dict]:
        """Converte tool schemas para formato de declarations (backward compat)."""
        return [
            {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}
            for t in tools
        ]

    def _to_langchain_messages(self, messages: list[dict]) -> list:
        """Converte mensagens dict para objetos LangChain."""
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            else:
                lc_messages.append(AIMessage(content=content))
        return lc_messages

    @staticmethod
    def _schemas_to_lc_tools(tools: list[dict]) -> list:
        """Converte tool schemas JSON para tool objects compatíveis com bind_tools."""
        lc_tools = []
        for t in tools:
            props = t.get("parameters", {}).get("properties", {})
            required = t.get("parameters", {}).get("required", [])

            # Monta JSON schema completo para bind_tools
            schema = {
                "title": t["name"],
                "description": t["description"],
                "type": "object",
                "properties": props,
            }
            if required:
                schema["required"] = required

            lc_tools.append(schema)
        return lc_tools
