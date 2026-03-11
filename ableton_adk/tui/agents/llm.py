"""LLM agent — routes natural language to tool calls via ADK runner."""

import asyncio
import os
from pathlib import Path

from .base import BaseAgent, ToolRegistry, AgentResponse


class LLMAgent:
    def __init__(self, registry: ToolRegistry):
        self._registry = registry

    def run(self, text: str) -> str:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent.parent / "ableton-config" / ".env")

        from google.adk.models.registry import _llm_registry_dict
        from google.adk.models.lite_llm import LiteLlm
        _llm_registry_dict["openrouter/.*"] = LiteLlm

        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        from ...agents.producer import producer_agent

        session_service = InMemorySessionService()
        runner = Runner(
            agent=producer_agent,
            app_name="margin_walker_tui",
            session_service=session_service,
        )

        loop = asyncio.new_event_loop()
        try:
            session = loop.run_until_complete(
                session_service.create_session(app_name="margin_walker_tui", user_id="tui")
            )
            user_msg = types.Content(role="user", parts=[types.Part(text=text)])

            parts = []
            async def collect():
                async for event in runner.run_async(
                    user_id="tui", session_id=session.id, new_message=user_msg
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                parts.append(part.text)
                            if part.function_call:
                                parts.append(f"  → {part.function_call.name}({dict(part.function_call.args)})")

            loop.run_until_complete(collect())
            return "\n".join(parts) if parts else "No response."
        finally:
            loop.close()
