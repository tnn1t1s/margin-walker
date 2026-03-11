from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class AgentResponse:
    message: str
    tool_calls: list[dict] = field(default_factory=list)
    error: bool = False


class ToolRegistry:
    def __init__(self):
        self._handlers: dict[str, Callable] = {}
        self._aliases: dict[str, str] = {}

    def register(self, name: str, handler: Callable, aliases: list[str] | None = None):
        self._handlers[name] = handler
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name

    def resolve(self, name: str) -> str:
        return self._aliases.get(name, name)

    def call(self, name: str, *args, **kwargs) -> Any:
        resolved = self.resolve(name)
        handler = self._handlers.get(resolved)
        if not handler:
            raise KeyError(f"Unknown command: {name}")
        return handler(*args, **kwargs)

    def list_commands(self) -> list[str]:
        return sorted(self._handlers.keys())


class BaseAgent:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    async def process(self, text: str) -> AgentResponse:
        raise NotImplementedError
