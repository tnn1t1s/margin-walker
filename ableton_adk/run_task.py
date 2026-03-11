#!/usr/bin/env python3
"""Run a direct task through the Ableton Producer agent."""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / "ableton-config" / ".env")

from google.adk.models.registry import _llm_registry_dict
from google.adk.models.lite_llm import LiteLlm

_llm_registry_dict["openrouter/.*"] = LiteLlm

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .agents.producer import producer_agent


async def run(task: str):
    session_service = InMemorySessionService()
    runner = Runner(
        agent=producer_agent,
        app_name="ableton_direct",
        session_service=session_service,
    )
    session = await session_service.create_session(
        app_name="ableton_direct", user_id="producer"
    )

    from google.genai import types

    user_msg = types.Content(role="user", parts=[types.Part(text=task)])

    async for event in runner.run_async(
        user_id="producer", session_id=session.id, new_message=user_msg
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
                if part.function_call:
                    print(f"  → {part.function_call.name}({dict(part.function_call.args)})")
                if part.function_response:
                    print(f"  ← {part.function_response.name}: {part.function_response.response}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = sys.stdin.read().strip()

    if not task:
        print("Usage: .venv/bin/python -m ableton_adk.run_task 'your task'", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run(task))
