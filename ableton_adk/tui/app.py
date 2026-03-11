"""margin-walker TUI — Ableton Live control surface."""

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import RichLog
from textual import work

from .widgets.command_input import CommandInput
from .widgets.status_bar import StatusBar
from .agents import ToolRegistry, DefaultAgent
from .commands import build_registry
from .macros import MacroStore


class MarginWalkerApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "margin-walker"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("f5", "play", "Play", show=True),
        Binding("f6", "stop", "Stop", show=True),
    ]

    def __init__(self):
        super().__init__()
        self._tool_registry = build_registry()
        reserved = set(self._tool_registry.list_commands())
        self._macro_store = MacroStore(reserved)
        self._tool_registry._macro_store = self._macro_store
        self._agent = DefaultAgent(self._tool_registry, self._macro_store)
        self._llm_agent = None

    def compose(self) -> ComposeResult:
        yield StatusBar(id="status")
        yield RichLog(id="output", highlight=True, markup=True, wrap=True)
        yield CommandInput(
            placeholder="/ command | free text for AI | /help",
            id="command",
        )

    def on_mount(self):
        self._refresh_status()
        output = self.query_one("#output", RichLog)
        output.write("[bold]margin-walker[/bold] — Ableton Live TUI")
        output.write("  /command for direct control | free text for AI agent | /help for commands")
        output.write("")
        self.query_one("#command", CommandInput).focus()

    def _refresh_status(self):
        try:
            from ..tools.song import get_song_info
            info = get_song_info()
            bar = self.query_one("#status", StatusBar)
            bar.tempo = info.get("tempo", 0)
            bar.playing = info.get("is_playing", False)
            bar.track_count = info.get("track_count", 0)
            bar.scene_count = info.get("scene_count", 0)
        except Exception:
            pass

    async def on_input_submitted(self, event) -> None:
        text = event.value.strip()
        if not text:
            return

        cmd_input = self.query_one("#command", CommandInput)
        cmd_input.add_to_history(text)
        cmd_input.value = ""

        output = self.query_one("#output", RichLog)

        if text.startswith("/"):
            output.write(f"[dim]> {text}[/dim]")

            stripped = text.lstrip("/").strip()
            if stripped.startswith("save "):
                self._handle_save(stripped[5:].strip(), output)
                return

            resp = await self._agent.process(text)
            style = "[red]" if resp.error else "[green]"
            output.write(f"{style}{resp.message}[/]")
            self._refresh_status()
        else:
            output.write(f"[dim]> {text}[/dim]")
            self._run_llm(text)

    @work(exclusive=True, thread=True)
    def _run_llm(self, text: str):
        output = self.query_one("#output", RichLog)
        try:
            agent = self._get_llm_agent()
            output.write("[yellow]thinking...[/yellow]")
            result = agent.run(text)
            output.write(f"[cyan]{result}[/cyan]")
        except Exception as e:
            output.write(f"[red]LLM error: {e}[/red]")
        self._refresh_status()

    def _handle_save(self, name: str, output: RichLog):
        if not name:
            output.write("[red]Usage: /save <name>[/red]")
            return
        if not self._llm_agent:
            output.write("[red]No LLM session yet — run a free-text command first[/red]")
            return
        prompt, steps = self._llm_agent.get_last_sequence()
        if not steps:
            output.write("[red]No tool calls to save — run a free-text command first[/red]")
            return
        err = self._macro_store.save(name, prompt, steps)
        if err:
            output.write(f"[red]{err}[/red]")
        else:
            output.write(f"[green]Saved macro '{name}' ({len(steps)} steps)[/green]")

    def action_play(self) -> None:
        output = self.query_one("#output", RichLog)
        try:
            from ..tools import transport
            transport.play()
            output.write("[green]▶ Playing[/green]")
        except Exception as e:
            output.write(f"[red]Play error: {e}[/red]")
        self._refresh_status()

    def action_stop(self) -> None:
        output = self.query_one("#output", RichLog)
        try:
            from ..tools import transport
            transport.stop()
            output.write("[green]■ Stopped[/green]")
        except Exception as e:
            output.write(f"[red]Stop error: {e}[/red]")
        self._refresh_status()

    def _get_llm_agent(self):
        if self._llm_agent is None:
            from .agents.llm import LLMAgent
            self._llm_agent = LLMAgent(self._tool_registry)
        return self._llm_agent


def main():
    app = MarginWalkerApp()
    app.run()


if __name__ == "__main__":
    main()
