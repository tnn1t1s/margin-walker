# TUI Research: Python Terminal Interface for Ableton Agent

## Framework Comparison

### Textual (Recommended)
- **Type**: Full TUI framework built on Rich, async-native (asyncio)
- **Strengths**: 16.7M colors, mouse support, 120 FPS rendering via segment tree delta updates, CSS-like styling, reactive attributes, built-in command palette with fuzzy search, worker system for background tasks, web browser deployment option
- **Weaknesses**: 35MB memory footprint (vs prompt_toolkit 25MB), steeper learning curve for simple use cases
- **Command Palette**: Built-in `Ctrl+P` palette with custom `Provider` classes. Define `COMMANDS = App.COMMANDS | {YourProvider}` on your App. Provider implements `search(query)` yielding `Hit` objects with score, display, and callback. Errors in providers don't crash the app.
- **Real-time Updates**: `run_worker` method and `@work` decorator run coroutines/threads in background. Worker events notify when complete. Ideal for streaming Ableton state via OSC/MIDI.
- **Chat/LLM Streaming**: `@work` decorator iterates response chunks, updates Markdown widget for streaming text effect. `VerticalScroll` container with `Input` widget at bottom.
- **Docs**: https://textual.textualize.io/

### prompt_toolkit
- **Type**: Low-level input library, GNU readline replacement
- **Strengths**: Fine-grained input control, hierarchical completions (router CLI-style), custom key bindings, Vi/Emacs modes, async support
- **Weaknesses**: Not a full TUI framework -- no layout engine, no widgets, no CSS. You build everything yourself.
- **Completions**: `Completer` class with `get_completions()` generator yielding `Completion` instances with text, position, and style. Supports nested/hierarchical completions for command trees.
- **Best For**: Input line only (embed inside Textual or use standalone for simple REPL)
- **Note**: cmd2 v4.0+ uses prompt_toolkit internally as its REPL engine
- **Docs**: https://python-prompt-toolkit.readthedocs.io/

### cmd2
- **Type**: Command interpreter framework extending stdlib `cmd`
- **Strengths**: Built-in pipe support (`|` to shell commands), file redirection, clipboard output, tab completion of commands/subcommands/paths, alias/macro creation, Python 3.10+
- **Weaknesses**: Not a visual TUI -- text-only command interpreter. No layout, no widgets, no real-time display panels.
- **Composable Commands**: Native pipe `|` support routes command output to shell. Aliases and macros for command abstraction.
- **Best For**: Unix-style composable command layer (could be embedded as command parser)
- **Docs**: https://cmd2.readthedocs.io/

### Rich + Click
- **Type**: Rich = rendering library, Click = CLI argument parser
- **Strengths**: Beautiful output formatting, composable CLI commands via Click groups
- **Weaknesses**: No interactivity, no REPL, no real-time updates. One-shot CLI tools only.
- **Best For**: Output formatting within another framework (Rich is Textual's foundation)

## Recommendation: Textual + cmd2 Hybrid

```
+-----------------------------------------------------------+
|  Textual App (full-screen TUI)                            |
|  +-----------------------------------------------------+  |
|  |  Status Bar: BPM | Track | Scene | Transport        |  |  <- Reactive widgets
|  +-----------------------------------------------------+  |
|  |  Main Panel (switchable)                             |  |
|  |  - Chat view (LLM conversation, Markdown rendering) |  |  <- VerticalScroll + Markdown
|  |  - Track view (mixer state, clip grid)               |  |  <- Custom widgets
|  |  - Log view (OSC/MIDI activity)                      |  |  <- RichLog widget
|  +-----------------------------------------------------+  |
|  |  Input Bar                                           |  |  <- Input widget
|  |  /command args   -> cmd2-style parser                |  |
|  |  free text       -> LLM conversation                 |  |
|  |  !shell cmd      -> shell execution                  |  |
|  +-----------------------------------------------------+  |
+-----------------------------------------------------------+
```

### Why This Architecture

1. **Textual** handles the visual layer: layout, widgets, real-time updates, theming, command palette
2. **cmd2-style parser** (or custom) handles slash command routing, pipe composition, tab completion
3. **prompt_toolkit** is unnecessary -- Textual's `Input` widget handles text entry, and cmd2 handles parsing
4. **Rich** comes free with Textual for formatted output

## Dual-Mode Input Design

### Input Routing Logic

```python
def on_input_submitted(self, event: Input.Submitted) -> None:
    text = event.value.strip()

    if not text:
        return

    if text.startswith("/"):
        # Command mode: parse and execute
        self.execute_command(text[1:])
    elif text.startswith("!"):
        # Shell mode: run command, capture output
        self.execute_shell(text[1:])
    elif "|" in text and text.split("|")[0].strip().startswith("/"):
        # Pipe mode: /tracks | /filter playing | /mute
        self.execute_pipeline(text)
    else:
        # Chat mode: send to LLM agent
        self.send_to_agent(text)
```

### Slash Command Registry Pattern

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Command:
    name: str
    handler: Callable
    description: str
    completions: list[str] | None = None

class CommandRegistry:
    def __init__(self):
        self._commands: dict[str, Command] = {}

    def register(self, name: str, description: str, completions=None):
        def decorator(fn):
            self._commands[name] = Command(name, fn, description, completions)
            return fn
        return decorator

    def parse(self, text: str) -> tuple[Command, list[str]] | None:
        parts = text.split()
        cmd_name = parts[0]
        args = parts[1:]
        if cmd := self._commands.get(cmd_name):
            return cmd, args
        return None

# Usage
registry = CommandRegistry()

@registry.register("stop", "Stop transport")
async def cmd_stop(app, args):
    await app.ableton.stop()

@registry.register("mute", "Mute track N", completions=["1","2","3"])
async def cmd_mute(app, args):
    track = int(args[0])
    await app.ableton.mute_track(track)

@registry.register("bpm", "Set BPM", completions=["120","128","140"])
async def cmd_bpm(app, args):
    await app.ableton.set_bpm(float(args[0]))
```

## Composable Command Pipeline

### Unix-Style Pipe Pattern

```python
class CommandPipeline:
    """Route output of one command as input to the next."""

    async def execute_pipeline(self, text: str):
        stages = [s.strip() for s in text.split("|")]
        data = None

        for stage in stages:
            if stage.startswith("/"):
                cmd, args = self.registry.parse(stage[1:])
                data = await cmd.handler(self, args, stdin=data)
            else:
                # Shell command receives piped data
                data = await self.shell_exec(stage, stdin=data)

        return data

# Example commands designed for piping:
# /tracks                -> list all tracks as JSON
# /tracks | /filter armed -> filter to armed tracks
# /tracks | /mute         -> mute all tracks
# /scenes | /launch 3     -> launch scene 3
```

### Command Categories for Ableton

```
Transport:  /play /stop /record /bpm <n>
Tracks:     /tracks /mute <n> /solo <n> /arm <n> /volume <n> <db>
Scenes:     /scenes /launch <n>
Clips:      /clips <track> /fire <track> <slot>
Mix:        /pan <n> <val> /send <track> <send> <val>
Agent:      /agent <prompt> /mode <creative|technical> /context
System:     /status /connect /disconnect /log /help
```

## Real-Time Ableton State Updates

### Worker Pattern for OSC/MIDI Monitoring

```python
from textual.app import App
from textual.reactive import reactive
from textual.worker import Worker

class AbletonTUI(App):
    bpm = reactive(120.0)
    is_playing = reactive(False)
    current_scene = reactive(0)

    def on_mount(self):
        # Background worker polls/listens for Ableton state
        self.run_worker(self.monitor_ableton, thread=True)

    async def monitor_ableton(self):
        """Long-running worker that listens for OSC messages."""
        async for msg in self.osc_listener:
            if msg.address == "/live/song/get/tempo":
                self.bpm = msg.args[0]
            elif msg.address == "/live/song/get/is_playing":
                self.is_playing = msg.args[0]

    def watch_bpm(self, value: float):
        """Called automatically when bpm changes."""
        self.query_one("#bpm-display").update(f"BPM: {value:.1f}")

    def watch_is_playing(self, value: bool):
        self.query_one("#transport").update("PLAY" if value else "STOP")
```

### Reactive Widget Binding

Textual's `reactive` attributes automatically trigger `watch_*` methods when values change. This maps directly to Ableton state: BPM, transport, track states, clip positions all become reactive properties that auto-update the UI.

## LLM/Agent Conversation Mode

### Streaming Chat Pattern

```python
from textual.widgets import Markdown, Input, Static
from textual.containers import VerticalScroll

class ChatView(VerticalScroll):

    def add_user_message(self, text: str):
        self.mount(Static(f"[bold]You:[/] {text}", classes="user-msg"))

    def add_agent_message(self) -> Markdown:
        widget = Markdown("", classes="agent-msg")
        self.mount(widget)
        self.scroll_end()
        return widget

    @work
    async def stream_response(self, prompt: str):
        self.add_user_message(prompt)
        widget = self.add_agent_message()

        buffer = ""
        async for chunk in self.agent.stream(prompt):
            buffer += chunk
            widget.update(buffer)
            self.scroll_end()
```

### Context Injection

The agent receives Ableton state as context:

```python
async def build_context(self) -> str:
    return f"""Current Ableton State:
- BPM: {self.app.bpm}
- Playing: {self.app.is_playing}
- Armed tracks: {await self.get_armed_tracks()}
- Current scene: {self.app.current_scene}

Available commands: {self.registry.list_commands()}
"""
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Textual | Only option with full TUI + async + command palette + CSS |
| Input parsing | Custom registry | cmd2 is overkill; simple prefix routing suffices |
| Completions | Textual command palette + inline | Ctrl+P for discovery, tab for inline |
| Real-time state | Textual reactive + workers | Native pattern, no polling loops needed |
| LLM chat | @work decorator + Markdown widget | Built-in streaming pattern |
| Pipe composition | Custom pipeline executor | Simple split-on-pipe with stdin chaining |
| Shell commands | `!` prefix (Claude Code pattern) | Familiar to users of Claude Code, vim |

## Reference Projects

- **PyChat.ai**: Rust+Python REPL with tab-to-switch between code and AI mode. Uses embedded Python interpreter + Gemini LLM.
- **LLM-Repl**: Built on langchain + rich. Conversation memory, simple REPL loop.
- **Claude Code**: Slash commands + conversation mode + ! shell prefix. Skills system with YAML frontmatter. Custom commands via .claude/commands/*.md files.
- **cmd2**: Pipe support, alias/macros, tab completion. Good reference for composable command patterns.

## Implementation Priority

1. **Phase 1**: Textual app shell with Input widget, dual-mode routing (/ commands vs chat)
2. **Phase 2**: Command registry with core Ableton commands (/stop, /play, /bpm, /mute)
3. **Phase 3**: Real-time status bar via reactive attributes + OSC worker
4. **Phase 4**: LLM agent chat with streaming responses
5. **Phase 5**: Pipe composition for command chaining
6. **Phase 6**: Command palette integration with fuzzy search

## Dependencies

```
textual>=1.0.0       # TUI framework
rich>=13.0.0         # Rendering (comes with textual)
python-osc>=1.8.0    # OSC communication with Ableton
# prompt_toolkit NOT needed -- textual handles input
# cmd2 NOT needed -- custom registry is simpler
```

## Sources

- [Textual Documentation](https://textual.textualize.io/)
- [Textual Command Palette Guide](https://textual.textualize.io/guide/command_palette/)
- [Textual Workers Guide](https://textual.textualize.io/guide/workers/)
- [7 Things Learned Building a Modern TUI Framework](https://www.textualize.io/blog/7-things-ive-learned-building-a-modern-tui-framework/)
- [prompt_toolkit Documentation](https://python-prompt-toolkit.readthedocs.io/)
- [cmd2 Documentation](https://cmd2.readthedocs.io/en/stable/)
- [Real Python - Textual Tutorial](https://realpython.com/python-textual/)
- [Building a Responsive Textual Chat UI](https://oneryalcin.medium.com/building-a-responsive-textual-chat-ui-with-long-running-processes-c0c53cd36224)
- [PyChat.ai - Python REPL with Agentic LLM](https://andreabergia.com/blog/2026/02/pychat-ai-a-live-python-repl-with-an-agentic-llm-that-edits-and-evaluates-code/)
- [10 Best Python TUI Libraries for 2025](https://medium.com/towards-data-engineering/10-best-python-text-user-interface-tui-libraries-for-2025-79f83b6ea16e)
- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Code Slash Commands](https://www.heyuan110.com/posts/ai/2026-03-05-claude-code-slash-commands/)
- [Textual vs prompt_toolkit Discussion](https://github.com/Textualize/textual/discussions/3254)
- [8 TUI Patterns for Python Apps](https://medium.com/@Nexumo_/8-tui-patterns-to-turn-python-scripts-into-apps-ce6f964d3b6f)
