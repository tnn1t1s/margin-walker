from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool

from .transport import (
    play, stop, toggle_record, get_tempo, set_tempo,
    get_time_signature, set_time_signature, get_is_playing, undo, redo,
)
from .track import (
    get_track_count, get_track_names, create_midi_track, create_audio_track,
    delete_track, set_track_name, set_track_arm, set_track_mute,
    set_track_solo, set_track_volume, set_track_pan, get_track_info,
)
from .clip import (
    create_clip, delete_clip, add_notes, get_notes, remove_notes,
    fire_clip, stop_clip, duplicate_clip, set_clip_name, set_clip_loop,
)
from .device import (
    get_device_count, get_device_names, get_device_parameters,
    set_device_parameter, set_device_enabled,
)
from .scene import (
    get_scene_count, get_scene_names, create_scene, delete_scene,
    fire_scene, set_scene_name, duplicate_scene,
)
from .mixer import (
    get_master_volume, set_master_volume, get_master_pan, get_master_devices,
    get_crossfader, set_crossfader, get_return_track_count, get_return_track_names,
    get_return_track_devices, set_return_volume, set_send_level, get_send_level,
)
from .song import (
    get_song_info, set_quantization, set_groove_amount,
    jump_to_time, get_current_time,
)


TOOL_DESCRIPTIONS = {
    "play": "Start playback.",
    "stop": "Stop playback.",
    "toggle_record": "Toggle session record.",
    "get_tempo": "Get current BPM.",
    "set_tempo": "Set BPM.",
    "get_time_signature": "Get time signature.",
    "set_time_signature": "Set time signature.",
    "get_is_playing": "Check if playing.",
    "undo": "Undo last action.",
    "redo": "Redo last action.",
    "get_track_count": "Get number of tracks.",
    "get_track_names": "Get all track names.",
    "create_midi_track": "Create MIDI track.",
    "create_audio_track": "Create audio track.",
    "delete_track": "Delete a track.",
    "set_track_name": "Rename a track.",
    "set_track_arm": "Arm/disarm track.",
    "set_track_mute": "Mute/unmute track.",
    "set_track_solo": "Solo/unsolo track.",
    "set_track_volume": "Set track volume.",
    "set_track_pan": "Set track pan.",
    "get_track_info": "Get track details.",
    "create_clip": "Create empty MIDI clip.",
    "delete_clip": "Delete a clip.",
    "add_notes": "Add MIDI notes to clip.",
    "get_notes": "Get notes from clip.",
    "remove_notes": "Remove notes from clip.",
    "fire_clip": "Launch a clip.",
    "stop_clip": "Stop a clip.",
    "duplicate_clip": "Duplicate a clip.",
    "set_clip_name": "Rename a clip.",
    "set_clip_loop": "Set clip loop points.",
    "get_device_count": "Get device count on track.",
    "get_device_names": "Get device names on track.",
    "get_device_parameters": "Get device parameters.",
    "set_device_parameter": "Set a device parameter.",
    "set_device_enabled": "Enable/bypass device.",
    "get_scene_count": "Get number of scenes.",
    "get_scene_names": "Get all scene names.",
    "create_scene": "Create a scene.",
    "delete_scene": "Delete a scene.",
    "fire_scene": "Launch a scene.",
    "set_scene_name": "Rename a scene.",
    "duplicate_scene": "Duplicate a scene.",
    "get_master_volume": "Get master volume.",
    "set_master_volume": "Set master volume.",
    "get_master_pan": "Get master panning.",
    "get_master_devices": "Get master track devices.",
    "get_crossfader": "Get crossfader position.",
    "set_crossfader": "Set crossfader position.",
    "get_return_track_count": "Get return track count.",
    "get_return_track_names": "Get return track names.",
    "get_return_track_devices": "Get return track devices.",
    "set_return_volume": "Set return track volume.",
    "set_send_level": "Set send level.",
    "get_send_level": "Get send level.",
    "get_song_info": "Get Live set overview.",
    "set_quantization": "Set launch quantization.",
    "set_groove_amount": "Set groove amount.",
    "jump_to_time": "Jump to beat position.",
    "get_current_time": "Get playback position.",
}

GROUPS = {
    "transport": [play, stop, toggle_record, get_tempo, set_tempo, get_time_signature, set_time_signature, get_is_playing, undo, redo],
    "track": [get_track_count, get_track_names, create_midi_track, create_audio_track, delete_track, set_track_name, set_track_arm, set_track_mute, set_track_solo, set_track_volume, set_track_pan, get_track_info],
    "clip": [create_clip, delete_clip, add_notes, get_notes, remove_notes, fire_clip, stop_clip, duplicate_clip, set_clip_name, set_clip_loop],
    "device": [get_device_count, get_device_names, get_device_parameters, set_device_parameter, set_device_enabled],
    "scene": [get_scene_count, get_scene_names, create_scene, delete_scene, fire_scene, set_scene_name, duplicate_scene],
    "mixer": [get_master_volume, set_master_volume, get_master_pan, get_master_devices, get_crossfader, set_crossfader, get_return_track_count, get_return_track_names, get_return_track_devices, set_return_volume, set_send_level, get_send_level],
    "song": [get_song_info, set_quantization, set_groove_amount, jump_to_time, get_current_time],
}


class _LeanFunctionTool(FunctionTool):
    def __init__(self, func, *, description):
        super().__init__(func)
        self._short_description = description


def _build_tools():
    tools = []
    for group_funcs in GROUPS.values():
        for func in group_funcs:
            desc = TOOL_DESCRIPTIONS[func.__name__]
            tools.append(_LeanFunctionTool(func, description=desc))
    return tools


class AbletonToolset(BaseToolset):
    def __init__(self):
        super().__init__()
        self._all_tools = _build_tools()

    async def get_tools(self, readonly_context=None):
        return self._all_tools
