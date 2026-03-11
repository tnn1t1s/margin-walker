from textual.widgets import Input
from textual.message import Message


class CommandInput(Input):

    class HistoryNav(Message):
        def __init__(self, direction: int):
            super().__init__()
            self.direction = direction

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history: list[str] = []
        self._hist_pos: int = -1
        self._saved_value: str = ""

    def _on_key(self, event):
        if event.key == "up":
            self._navigate_history(1)
            event.prevent_default()
            event.stop()
        elif event.key == "down":
            self._navigate_history(-1)
            event.prevent_default()
            event.stop()
        else:
            super()._on_key(event)

    def add_to_history(self, text: str):
        if text and (not self._history or self._history[-1] != text):
            self._history.append(text)
        self._hist_pos = -1

    def _navigate_history(self, direction: int):
        if not self._history:
            return
        if self._hist_pos == -1:
            self._saved_value = self.value
        new_pos = self._hist_pos + direction
        if new_pos < 0:
            self._hist_pos = -1
            self.value = self._saved_value
            return
        if new_pos >= len(self._history):
            return
        self._hist_pos = new_pos
        idx = len(self._history) - 1 - new_pos
        self.value = self._history[idx]
