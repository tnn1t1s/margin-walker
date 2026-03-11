"""Command registry — maps slash commands to tool functions."""

from ..tools import transport, track, clip, device, scene, mixer, song
from .agents.base import ToolRegistry


def build_registry() -> ToolRegistry:
    reg = ToolRegistry()

    # transport
    reg.register("play", lambda: transport.play(), ["p"])
    reg.register("stop", lambda: transport.stop(), ["x"])
    reg.register("rec", lambda: transport.toggle_record())
    reg.register("tempo", lambda *a: _tempo(*a), ["bpm"])
    reg.register("undo", lambda: transport.undo())
    reg.register("redo", lambda: transport.redo())

    # track — mute/solo/arm accept track index or name fragment
    reg.register("mute", lambda *a: _mute(*a), ["m"])
    reg.register("unmute", lambda *a: _unmute(*a))
    reg.register("solo", lambda *a: _solo(*a), ["s"])
    reg.register("unsolo", lambda *a: _unsolo(*a))
    reg.register("arm", lambda *a: _arm(*a))
    reg.register("vol", lambda *a: _vol(*a), ["v"])
    reg.register("pan", lambda *a: _pan(*a))
    reg.register("tracks", lambda: track.get_track_names(), ["ls"])
    reg.register("info", lambda *a: _info(*a), ["i"])

    # scene
    reg.register("scenes", lambda: scene.get_scene_names())
    reg.register("fire", lambda *a: _fire_scene(*a), ["f"])

    # clip
    reg.register("launch", lambda *a: _fire_clip(*a), ["l"])

    # mixer
    reg.register("master", lambda: mixer.get_master_volume())
    reg.register("returns", lambda: _returns())
    reg.register("send", lambda *a: _send(*a))

    # song
    reg.register("status", lambda: song.get_song_info(), ["st"])
    reg.register("devices", lambda *a: _devices(*a), ["d"])

    # meta
    reg.register("help", lambda: _help(reg), ["h", "?"])

    return reg


def _resolve_track(ident: str) -> int:
    names = track.get_track_names()["tracks"]
    ident_lower = ident.lower().replace(" ", "")
    for t in names:
        name_compressed = t["name"].lower().replace(" ", "").replace("-", "")
        if ident_lower in name_compressed:
            return t["index"]
    try:
        return int(ident)
    except ValueError:
        raise ValueError(f"No track matching '{ident}'")


def _tempo(*args):
    if args:
        return transport.set_tempo(float(args[0]))
    return transport.get_tempo()


def _mute(*args):
    if not args:
        return "Usage: /mute <track>"
    idx = _resolve_track(args[0])
    return track.set_track_mute(idx, True)


def _unmute(*args):
    if not args:
        return "Usage: /unmute <track>"
    idx = _resolve_track(args[0])
    return track.set_track_mute(idx, False)


def _solo(*args):
    if not args:
        return "Usage: /solo <track>"
    idx = _resolve_track(args[0])
    return track.set_track_solo(idx, True)


def _unsolo(*args):
    if not args:
        return "Usage: /unsolo <track>"
    idx = _resolve_track(args[0])
    return track.set_track_solo(idx, False)


def _arm(*args):
    if not args:
        return "Usage: /arm <track>"
    idx = _resolve_track(args[0])
    armed = True
    if len(args) > 1 and args[1].lower() in ("off", "0", "false"):
        armed = False
    return track.set_track_arm(idx, armed)


def _vol(*args):
    if len(args) < 2:
        if args:
            idx = _resolve_track(args[0])
            return track.get_track_info(idx)
        return "Usage: /vol <track> <0.0-1.0>"
    idx = _resolve_track(args[0])
    return track.set_track_volume(idx, float(args[1]))


def _pan(*args):
    if len(args) < 2:
        return "Usage: /pan <track> <-1.0 to 1.0>"
    idx = _resolve_track(args[0])
    return track.set_track_pan(idx, float(args[1]))


def _info(*args):
    if not args:
        return song.get_song_info()
    idx = _resolve_track(args[0])
    return track.get_track_info(idx)


def _fire_scene(*args):
    if not args:
        return "Usage: /fire <scene_index>"
    return scene.fire_scene(int(args[0]))


def _fire_clip(*args):
    if len(args) < 2:
        return "Usage: /launch <track> <scene>"
    t = _resolve_track(args[0])
    return clip.fire_clip(t, int(args[1]))


def _returns():
    try:
        names = mixer.get_return_track_names()
        count = mixer.get_return_track_count()
        return {**count, **names}
    except Exception:
        return mixer.get_return_track_count()


def _send(*args):
    if len(args) < 3:
        return "Usage: /send <track> <send_index> <level>"
    t = _resolve_track(args[0])
    return mixer.set_send_level(t, int(args[1]), float(args[2]))


def _devices(*args):
    if not args:
        return "Usage: /devices <track>"
    idx = _resolve_track(args[0])
    return device.get_device_names(idx)


def _help(reg: ToolRegistry) -> str:
    cmds = reg.list_commands()
    return "Commands: " + " ".join(f"/{c}" for c in cmds)
