from google.adk.agents import LlmAgent
from ..prompts import MIXER_INSTRUCTION
from ..tools import AbletonToolset

mixer_agent = LlmAgent(
    name="mixer",
    model="openrouter/anthropic/claude-haiku-4-5-20251001",
    instruction=MIXER_INSTRUCTION,
    tools=[AbletonToolset()],
    output_key="mix_results",
    description="Handles mixing, levels, and effects.",
)
