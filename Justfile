set dotenv-load := false

PYTHON := ".venv/bin/python"
ADK := ".venv/bin/adk"
REMOTE_SCRIPTS := ~/Music/Ableton/User\ Library/Remote\ Scripts

setup-venv:
    python3 -m venv .venv
    .venv/bin/pip install -e ".[dev]"

setup-osc:
    git submodule update --init --recursive
    mkdir -p {{REMOTE_SCRIPTS}}
    ln -sfn "$(pwd)/AbletonOSC" {{REMOTE_SCRIPTS}}/AbletonOSC
    @echo "AbletonOSC symlinked → {{REMOTE_SCRIPTS}}/AbletonOSC"
    @echo "Restart Ableton → Preferences → Link/Tempo/MIDI → Control Surface: AbletonOSC"

setup: setup-venv setup-osc

update-osc:
    git submodule update --remote AbletonOSC
    @echo "AbletonOSC updated. Restart Ableton to pick up changes."

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
