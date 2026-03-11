set dotenv-load := false

PYTHON := ".venv/bin/python"
ADK := ".venv/bin/adk"

setup-venv:
    python3 -m venv .venv
    .venv/bin/pip install -e ".[dev]"

run:
    {{ADK}} run .

web:
    {{ADK}} web .

task TASK:
    {{PYTHON}} -m ableton_adk.run_task "{{TASK}}"

test:
    {{PYTHON}} -m pytest tests/ -v

check-osc:
    {{PYTHON}} -c "from ableton_adk.lib import get_client; c = get_client(); print(c.query('/live/song/get/tempo'))"
