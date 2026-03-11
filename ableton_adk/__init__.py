from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from google.adk.agents import SequentialAgent
from google.adk.models.registry import _llm_registry_dict
from google.adk.models.lite_llm import LiteLlm

_llm_registry_dict["openrouter/.*"] = LiteLlm

from .agents import composer_agent, producer_agent, mixer_agent

root_agent = SequentialAgent(
    name="ableton_producer",
    description="AI music production pipeline for Ableton Live. Composes, produces, and mixes music.",
    sub_agents=[composer_agent, producer_agent, mixer_agent],
)
