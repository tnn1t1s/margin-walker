from google.adk.agents import LlmAgent
from ..prompts import PRODUCER_INSTRUCTION
from ..tools import AbletonToolset

producer_agent = LlmAgent(
    name="producer",
    model="openrouter/anthropic/claude-sonnet-4-5",
    instruction=PRODUCER_INSTRUCTION,
    tools=[AbletonToolset()],
    output_key="production_results",
    description="Executes production actions in Ableton Live.",
)
