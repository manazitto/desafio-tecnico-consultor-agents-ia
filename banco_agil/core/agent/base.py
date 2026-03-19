"""Base Agent e sistema de tools."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    """Representa uma ferramenta que um agente pode usar."""
    name: str
    description: str
    parameters: dict
    handler: Callable[..., Any]

    def to_schema(self) -> dict:
        """Converte para JSON schema compativel com LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


@dataclass
class HandoffSignal:
    """Sinal para transferencia entre agentes."""
    target_agent: str
    context: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Contrato base para todos os agentes do sistema."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identificador unico do agente."""
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Instrucoes do agente para o LLM."""
        ...

    @property
    @abstractmethod
    def tools(self) -> list[Tool]:
        """Lista de ferramentas disponiveis para o agente."""
        ...

    def get_tools_map(self) -> dict[str, Callable]:
        """Retorna mapa nome -> handler para execucao de tools."""
        return {tool.name: tool.handler for tool in self.tools}

    def get_tools_schemas(self) -> list[dict]:
        """Retorna schemas JSON de todas as tools."""
        return [tool.to_schema() for tool in self.tools]
