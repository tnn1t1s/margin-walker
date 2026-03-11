import shlex
from .base import BaseAgent, ToolRegistry, AgentResponse


class DefaultAgent(BaseAgent):
    async def process(self, text: str) -> AgentResponse:
        text = text.lstrip("/").strip()
        if not text:
            return AgentResponse(message="", error=True)

        # pipe support: /mute 0 | /mute 1 | /mute 2
        if "|" in text:
            return await self._process_pipeline(text)

        try:
            parts = shlex.split(text)
        except ValueError as e:
            return AgentResponse(message=str(e), error=True)

        cmd = parts[0].lower()
        args = parts[1:]

        try:
            result = self.registry.call(cmd, *args)
            msg = self._format_result(cmd, result)
            return AgentResponse(message=msg, tool_calls=[{"tool": cmd, "args": args}])
        except KeyError:
            return AgentResponse(message=f"Unknown: /{cmd}. Type /help for commands.", error=True)
        except Exception as e:
            return AgentResponse(message=f"Error: {e}", error=True)

    async def _process_pipeline(self, text: str) -> AgentResponse:
        segments = [s.strip() for s in text.split("|") if s.strip()]
        results = []
        for segment in segments:
            resp = await self.process("/" + segment if not segment.startswith("/") else segment)
            results.append(resp.message)
            if resp.error:
                return AgentResponse(message=" | ".join(results), error=True)
        return AgentResponse(message=" | ".join(results))

    def _format_result(self, cmd: str, result) -> str:
        if isinstance(result, dict):
            parts = [f"{k}={v}" for k, v in result.items() if v is not None]
            return " ".join(parts) if parts else "ok"
        return str(result) if result is not None else "ok"
