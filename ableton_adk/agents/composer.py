from google.adk.agents import LlmAgent
from ..prompts import COMPOSER_INSTRUCTION
from ..tools import AbletonToolset

composer_agent = LlmAgent(
    name="composer",
    model="openrouter/anthropic/claude-sonnet-4-5",
    instruction=COMPOSER_INSTRUCTION,
    tools=[AbletonToolset()],
    output_key="composition_plan",
    description="Interprets music requests and creates production plans.",
)
