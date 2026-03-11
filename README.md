# margin-walker

AI agents for Ableton Live, built on [Google ADK](https://github.com/google/adk-python) and [AbletonOSC](https://github.com/ideoforms/AbletonOSC).

Three-agent pipeline that interprets music requests, executes production actions, and mixes — all through natural language.

```
Composer (Sonnet) → Producer (Sonnet) → Mixer (Haiku)
    plan               execute             mix
```

## Architecture

```
margin-walker/
├── ableton_adk/
│   ├── agents/          # Composer, Producer, Mixer
│   ├── tools/           # 53 OSC tools across 7 modules
│   │   ├── transport    # play, stop, tempo, time sig
│   │   ├── track        # create, arm, mute, solo, volume, pan
│   │   ├── clip         # create, add MIDI notes, fire, loop
│   │   ├── device       # parameters, enable/bypass
│   │   ├── scene        # create, fire, duplicate
│   │   ├── mixer        # master, returns, sends, crossfader
│   │   └── song         # info, quantization, groove
│   ├── prompts/         # Agent instructions
│   └── lib/
│       └── osc_client   # UDP client (send:11000, recv:11001)
├── AbletonOSC/          # Submodule (with custom master/return handlers)
├── ableton-config/      # Your API keys + agent instructions
└── docs/                # Integration research
```

### Custom AbletonOSC Extensions

We add two handlers missing from upstream AbletonOSC:

- **MasterTrackHandler** — `/live/master/get|set/{volume,panning,crossfader}`, device listing
- **ReturnTrackHandler** — `/live/return/get|set/{volume,panning,send}`, `/live/song/get/num_return_tracks`

## Setup

```bash
# 1. Clone with submodules
git clone --recurse-submodules https://github.com/tnn1t1s/margin-walker.git
cd margin-walker

# 2. Install
just setup

# 3. Configure
cp ableton-config.example/.env ableton-config/.env
# Edit ableton-config/.env with your OPENROUTER_API_KEY

# 4. In Ableton Live
# Preferences → Link/Tempo/MIDI → Control Surface: AbletonOSC

# 5. Verify connection
just check-osc
```

## Usage

```bash
# Full pipeline (Composer → Producer → Mixer)
just run

# Browser UI
just web

# Direct task to Producer agent
just task "create a 4-bar drum loop at 120bpm"
just task "add a bassline on track 2 using C2 and G1"
just task "set all chord tracks to 50% volume and pan them L/C/R"
```

### Python

```python
from ableton_adk.tools.track import get_track_names, set_track_volume
from ableton_adk.tools.transport import play, set_tempo
from ableton_adk.tools.clip import create_clip, add_notes

set_tempo(124.0)
create_clip(track_index=0, scene_index=0, length=4.0)
add_notes(0, 0, [
    {"pitch": 36, "start": 0.0, "duration": 0.5, "velocity": 100},  # kick
    {"pitch": 36, "start": 1.0, "duration": 0.5, "velocity": 100},
    {"pitch": 36, "start": 2.0, "duration": 0.5, "velocity": 100},
    {"pitch": 36, "start": 3.0, "duration": 0.5, "velocity": 100},
])
play()
```

## Requirements

- Ableton Live 11 or 12
- Python 3.12+
- [just](https://github.com/casey/just) command runner
- OpenRouter API key (for agent LLM calls)

## License

MIT
