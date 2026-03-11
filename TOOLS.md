# TOOLS.md — Ableton ADK Tool Contract

## Transport
| Tool | Args | Returns |
|------|------|---------|
| `play` | — | `{status}` |
| `stop` | — | `{status}` |
| `toggle_record` | — | `{status}` |
| `get_tempo` | — | `{tempo}` |
| `set_tempo` | `bpm: float` | `{tempo}` |
| `get_time_signature` | — | `{numerator, denominator}` |
| `set_time_signature` | `numerator: int, denominator: int` | `{numerator, denominator}` |
| `get_is_playing` | — | `{is_playing}` |
| `undo` | — | `{status}` |
| `redo` | — | `{status}` |

## Track
| Tool | Args | Returns |
|------|------|---------|
| `get_track_count` | — | `{count}` |
| `get_track_names` | — | `{tracks: [{index, name}]}` |
| `create_midi_track` | `index: int=-1` | `{status, index}` |
| `create_audio_track` | `index: int=-1` | `{status, index}` |
| `delete_track` | `track_index: int` | `{status, track_index}` |
| `set_track_name` | `track_index: int, name: str` | `{status, track_index, name}` |
| `set_track_arm` | `track_index: int, armed: bool=True` | `{track_index, armed}` |
| `set_track_mute` | `track_index: int, muted: bool=True` | `{track_index, muted}` |
| `set_track_solo` | `track_index: int, solo: bool=True` | `{track_index, solo}` |
| `set_track_volume` | `track_index: int, volume: float` | `{track_index, volume}` |
| `set_track_pan` | `track_index: int, pan: float` | `{track_index, pan}` |
| `get_track_info` | `track_index: int` | `{track_index, name, armed, muted, solo, volume, pan}` |

## Clip
| Tool | Args | Returns |
|------|------|---------|
| `create_clip` | `track_index: int, scene_index: int, length: float=4.0` | `{status, track_index, scene_index, length}` |
| `delete_clip` | `track_index: int, scene_index: int` | `{status, track_index, scene_index}` |
| `add_notes` | `track_index: int, scene_index: int, notes: [{pitch, start, duration, velocity?, mute?}]` | `{status, count}` |
| `get_notes` | `track_index: int, scene_index: int` | `{notes: [{pitch, start, duration, velocity, mute}]}` |
| `remove_notes` | `track_index: int, scene_index: int, from_time?, time_span?, from_pitch?, pitch_span?` | `{status}` |
| `fire_clip` | `track_index: int, scene_index: int` | `{status}` |
| `stop_clip` | `track_index: int, scene_index: int` | `{status}` |
| `duplicate_clip` | `track_index: int, scene_index: int` | `{status, source_scene, target_scene}` |
| `set_clip_name` | `track_index: int, scene_index: int, name: str` | `{status, name}` |
| `set_clip_loop` | `track_index: int, scene_index: int, loop_start?, loop_end?` | `{status, loop_start, loop_end}` |

## Device
| Tool | Args | Returns |
|------|------|---------|
| `get_device_count` | `track_index: int` | `{track_index, count}` |
| `get_device_names` | `track_index: int` | `{track_index, devices: [{index, name}]}` |
| `get_device_parameters` | `track_index: int, device_index: int` | `{parameters: [{index, name, value, min, max}]}` |
| `set_device_parameter` | `track_index: int, device_index: int, parameter_index: int, value: float` | `{status}` |
| `set_device_enabled` | `track_index: int, device_index: int, enabled: bool=True` | `{enabled}` |

## Scene
| Tool | Args | Returns |
|------|------|---------|
| `get_scene_count` | — | `{count}` |
| `get_scene_names` | — | `{scenes: [{index, name}]}` |
| `create_scene` | `index: int=-1` | `{status, index}` |
| `delete_scene` | `scene_index: int` | `{status, scene_index}` |
| `fire_scene` | `scene_index: int` | `{status, scene_index}` |
| `set_scene_name` | `scene_index: int, name: str` | `{status, scene_index, name}` |
| `duplicate_scene` | `scene_index: int` | `{status, scene_index}` |

## Mixer
| Tool | Args | Returns |
|------|------|---------|
| `get_master_volume` | — | `{master_volume}` |
| `set_master_volume` | `volume: float` | `{master_volume}` |
| `get_return_track_count` | — | `{count}` |
| `set_send_level` | `track_index: int, send_index: int, level: float` | `{track_index, send_index, level}` |
| `get_send_level` | `track_index: int, send_index: int` | `{level}` |
| `set_crossfader` | `position: float` | `{crossfader}` |

## Song
| Tool | Args | Returns |
|------|------|---------|
| `get_song_info` | — | `{tempo, time_signature, track_count, scene_count, is_playing}` |
| `set_quantization` | `value: int` | `{quantization}` |
| `set_groove_amount` | `amount: float` | `{groove_amount}` |
| `jump_to_time` | `time_beats: float` | `{position}` |
| `get_current_time` | — | `{time_beats}` |

## Protocol
All tools communicate via OSC to AbletonOSC (port 11000 send, 11001 receive).
Requires AbletonOSC MIDI Remote Script installed in Ableton Live.
