# AbletonOSC - OSC Control for Ableton Live

## What It Is

AbletonOSC is a MIDI Remote Script that provides an Open Sound Control (OSC) interface to control Ableton Live. It exposes the entire Live Object Model (LOM) API via OSC, using the same naming structure and object hierarchy as the native LOM. This is the most comprehensive OSC interface available for Ableton Live.

- **Repository**: https://github.com/ideoforms/AbletonOSC
- **Status**: Beta
- **Requirements**: Ableton Live 11 or above
- **Author**: Daniel Jones (ideoforms)
- **License**: MIT

## How It Works

### Protocol / Architecture

```
┌─────────────────┐     OSC (UDP)      ┌───────────────────┐
│  Client App     │ ──────────────────> │  AbletonOSC       │
│  (Python, JS,   │    port 11000       │  (Remote Script    │
│   TouchOSC,     │ <────────────────── │   inside Live)     │
│   any OSC app)  │    port 11001       │                    │
└─────────────────┘                     └───────────────────┘
```

- **Listen Port**: 11000 (receives OSC messages)
- **Reply Port**: 11001 (sends responses to originating IP)
- OSC wildcard patterns supported (e.g., `/live/clip/get/* 0 0`)
- Replies are sent to the same IP as the originating message

## Installation / Setup

1. Download the repository as a ZIP and unzip
2. Rename the folder from `AbletonOSC-master` to `AbletonOSC`
3. Copy to the Remote Scripts directory:
   - **macOS**: `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows**: `\Users\[username]\Documents\Ableton\User Library\Remote Scripts`
4. Restart Ableton Live
5. In Preferences > Link/Tempo/MIDI, select "AbletonOSC" from the Control Surface dropdown

Activity logs are written to a `logs` subdirectory within the AbletonOSC folder.

## Key API Endpoints

### Application API

| Address | Description |
|---------|-------------|
| `/live/test` | Confirmation test |
| `/live/application/get/version` | Query Live version |
| `/live/api/reload` | Reload server code |
| `/live/api/set/log_level` | Set log level (debug/info/warning/error/critical) |
| `/live/api/show_message` | Display message in Live's status bar |

Status messages:
- `/live/startup` -- Sent when AbletonOSC initializes
- `/live/error` -- Error notifications

### Song API (Transport & Session)

**Methods:**

| Address | Description |
|---------|-------------|
| `/live/song/start_playing` | Start playback |
| `/live/song/stop_playing` | Stop playback |
| `/live/song/continue_playing` | Continue from current position |
| `/live/song/stop_all_clips` | Stop all clips |
| `/live/song/create_audio_track` | Create audio track (args: index) |
| `/live/song/create_midi_track` | Create MIDI track (args: index) |
| `/live/song/create_return_track` | Create return track |
| `/live/song/create_scene` | Create scene (args: index) |
| `/live/song/delete_scene` | Delete scene (args: index) |
| `/live/song/duplicate_scene` | Duplicate scene (args: index) |
| `/live/song/jump_by` | Jump by beats (args: beats) |
| `/live/song/jump_to_next_cue` | Jump to next cue point |
| `/live/song/jump_to_prev_cue` | Jump to previous cue point |
| `/live/song/tap_tempo` | Tap tempo |
| `/live/song/undo` | Undo |
| `/live/song/redo` | Redo |

**Properties (get/set):**

| Property | Type | Description |
|----------|------|-------------|
| `is_playing` | bool | Playback state |
| `tempo` | float | Tempo in BPM |
| `current_song_time` | float | Current position |
| `loop` | bool | Loop enabled |
| `loop_start` | float | Loop start position |
| `loop_length` | float | Loop length |
| `metronome` | bool | Metronome on/off |
| `record_mode` | bool | Recording state |
| `session_record` | bool | Session recording |
| `arrangement_overdub` | bool | Arrangement overdub |
| `signature_numerator` | int | Time signature numerator |
| `signature_denominator` | int | Time signature denominator |
| `clip_trigger_quantization` | int | Clip trigger quantization |
| `midi_recording_quantization` | int | MIDI recording quantization |

**Collection Queries:**

| Address | Description |
|---------|-------------|
| `/live/song/get/num_tracks` | Number of tracks |
| `/live/song/get/num_scenes` | Number of scenes |
| `/live/song/get/track_names` | All track names |
| `/live/song/get/cue_points` | All cue points with metadata |

**Bulk Data:**
```
/live/song/get/track_data 0 12 track.name clip.name clip.length
```
Returns properties for tracks 0-11 with specified attributes.

**Beat Events:**
```
/live/song/start_listen/beat    # Subscribe to beat notifications
/live/song/stop_listen/beat     # Unsubscribe
```

### Track API

All track endpoints require a `track_id` parameter.

**Properties (get/set):**

| Property | Type | Description |
|----------|------|-------------|
| `arm` | 0/1 | Record arm |
| `mute` | 0/1 | Mute state |
| `solo` | 0/1 | Solo state |
| `volume` | float | Track volume |
| `panning` | float | Pan position |
| `name` | string | Track name |
| `color` | int | Track color |
| `color_index` | int | Color index |
| `send` | float | Send level (requires send_id) |
| `current_monitoring_state` | int | Monitoring mode |
| `fold_state` | int | Group fold state |
| `input_routing_type` | string | Input routing |
| `output_routing_type` | string | Output routing |

**Read-only Properties:**

| Property | Description |
|----------|-------------|
| `output_meter_left` | Left output meter level |
| `output_meter_right` | Right output meter level |
| `output_meter_level` | Combined output level |
| `is_grouped` | Whether track is in a group |
| `is_foldable` | Whether track can be folded |
| `has_midi_input` | Has MIDI input |
| `has_audio_input` | Has audio input |
| `playing_slot_index` | Currently playing clip slot |
| `fired_slot_index` | Triggered clip slot |
| `can_be_armed` | Whether track supports arming |

**Listeners:**
```
/live/track/start_listen/[property] [track_id]
/live/track/stop_listen/[property] [track_id]
```

### View API

| Address | Description |
|---------|-------------|
| `/live/view/get/selected_scene` | Get selected scene index |
| `/live/view/get/selected_track` | Get selected track index |
| `/live/view/get/selected_clip` | Get selected clip (track, scene) |
| `/live/view/get/selected_device` | Get selected device (track, device) |
| `/live/view/set/selected_scene` | Set scene selection |
| `/live/view/set/selected_track` | Set track selection |
| `/live/view/set/selected_clip` | Set clip selection |
| `/live/view/set/selected_device` | Set device selection |

### Clip API

Clip endpoints require `track_id` and `clip_id` parameters.

Properties include: `name`, `length`, `color`, `is_playing`, `is_recording`, `looping`, `loop_start`, `loop_end`, `start_marker`, `end_marker`, `gain`, `pitch_coarse`, `pitch_fine`, `warp_mode`.

### Clip Slot API

| Address | Description |
|---------|-------------|
| `/live/clip_slot/create_clip` | Create clip (track, scene, length) |
| `/live/clip_slot/delete_clip` | Delete clip (track, scene) |
| `/live/clip_slot/duplicate_clip_to` | Duplicate clip to target |

### Device API

Device endpoints require `track_id` and `device_id`.

| Address | Description |
|---------|-------------|
| `/live/device/get/name` | Device name |
| `/live/device/get/type` | Device type |
| `/live/device/get/num_parameters` | Parameter count |
| `/live/device/get/parameters/name` | All parameter names |
| `/live/device/get/parameters/value` | All parameter values |
| `/live/device/get/parameters/min` | All parameter minimums |
| `/live/device/get/parameters/max` | All parameter maximums |
| `/live/device/set/parameters/value` | Set parameter values |

## Code Examples

### Python (using python-osc)

```python
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 11000)

# Set tempo
client.send_message("/live/song/set/tempo", [128.0])

# Start playback
client.send_message("/live/song/start_playing", [])

# Create a MIDI track at index 0
client.send_message("/live/song/create_midi_track", [0])

# Arm track 0
client.send_message("/live/track/set/arm", [0, 1])

# Set track volume
client.send_message("/live/track/set/volume", [0, 0.85])

# Create a clip in track 0, scene 0, 4 beats long
client.send_message("/live/clip_slot/create_clip", [0, 0, 4.0])

# Fire a clip
client.send_message("/live/clip/fire", [0, 0])

# Query tempo (response comes on port 11001)
client.send_message("/live/song/get/tempo", [])

# Query all track names
client.send_message("/live/song/get/track_names", [])
```

### Receiving OSC Responses (Python)

```python
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def handle_tempo(address, *args):
    print(f"Tempo: {args[0]}")

def handle_beat(address, *args):
    print(f"Beat: {args[0]}")

dispatcher = Dispatcher()
dispatcher.map("/live/song/get/tempo", handle_tempo)
dispatcher.map("/live/song/get/beat", handle_beat)

server = BlockingOSCUDPServer(("127.0.0.1", 11001), dispatcher)
server.serve_forever()
```

### Console Utility

AbletonOSC includes a command-line console (`run-console.py`):

```bash
python run-console.py

# In the console:
> /live/song/get/tempo
> /live/song/set/tempo 140
> /live/clip/get/* 0 0    # Wildcard - get all properties
```

## Related Projects

- **pylive**: Python framework that uses AbletonOSC as its transport layer -- https://github.com/ideoforms/pylive
- **ableton-live-mcp-server**: MCP Server for AI assistant control via AbletonOSC -- https://github.com/Simon-Kansara/ableton-live-mcp-server
- **ableton-osc-mcp**: Another MCP server for Ableton via OSC -- https://github.com/nozomi-koborinai/ableton-osc-mcp
- **LiveOSC**: Older OSC interface (predecessor) -- https://github.com/hanshuebner/LiveOSC

## Links

- **Repository**: https://github.com/ideoforms/AbletonOSC
- **Live Object Model docs**: https://docs.cycling74.com/max8/vignettes/live_object_model
- **python-osc library**: https://pypi.org/project/python-osc/
