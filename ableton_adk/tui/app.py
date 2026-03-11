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


class MarginWalkerApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "margin-walker"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    def __init__(self):
        super().__init__()
        self._registry = build_registry()
        self._agent = DefaultAgent(self._registry)
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

    def _get_llm_agent(self):
        if self._llm_agent is None:
            from .agents.llm import LLMAgent
            self._llm_agent = LLMAgent(self._registry)
        return self._llm_agent


def main():
    app = MarginWalkerApp()
    app.run()


if __name__ == "__main__":
    main()
