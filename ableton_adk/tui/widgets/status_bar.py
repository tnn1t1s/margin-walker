from textual.widgets import Static
from textual.reactive import reactive


class StatusBar(Static):
    tempo = reactive(0.0)
    playing = reactive(False)
    track_count = reactive(0)
    scene_count = reactive(0)

    def render(self) -> str:
        state = "PLAY" if self.playing else "STOP"
        return f" {self.tempo:.0f} BPM | {state} | {self.track_count} tracks | {self.scene_count} scenes"

    def watch_tempo(self, _):
        self.refresh()

    def watch_playing(self, _):
        self.refresh()

    def watch_track_count(self, _):
        self.refresh()

    def watch_scene_count(self, _):
        self.refresh()
