# Python Libraries for Ableton Live Control

## Overview

Several Python libraries exist for controlling Ableton Live, ranging from high-level frameworks to low-level TCP socket interfaces. The two most significant are **pylive** (OSC-based, high-level) and **ableton-liveapi-tools** (TCP socket, comprehensive).

---

## pylive

### What It Is

pylive is a Python framework for querying and controlling Ableton Live from a standalone Python script, mediated via Open Sound Control (OSC). It mirrors the Control Surface API, allowing developers to manipulate Live parameters without sending MIDI note data.

- **Repository**: https://github.com/ideoforms/pylive
- **PyPI**: https://pypi.org/project/pylive/
- **Stars**: 616 | **Forks**: 76
- **Author**: Daniel Jones (ideoforms) -- same author as AbletonOSC
- **Requirements**: Ableton Live 11+, Python 3.7+, AbletonOSC (required dependency)

### Installation

```bash
# From PyPI
pip3 install pylive

# From source
git clone https://github.com/ideoforms/pylive.git
cd pylive
python3 setup.py install

# Verify
python3 setup.py test
```

**Prerequisite**: AbletonOSC must be installed and active in Ableton Live (see 02-ableton-osc.md).

### API Classes

#### Set (Live Session)

```python
import live

# Initialize - scan=True queries all tracks, clips, devices
set = live.Set(scan=True)

# Properties
set.tempo           # float - get/set tempo
set.tempo = 120.0   # set tempo
set.time            # float - current song time
set.overdub         # bool - overdub state

# Collections
set.tracks          # list of Track objects

# Caching (enable when no external processes modify Live)
set.caching = True  # cache property values locally
```

#### Track

```python
track = set.tracks[0]

# Properties
track.name          # str - track name
track.mute          # bool - mute state
track.mute = True   # set mute

# Collections
track.clips         # list of Clip objects
track.devices       # list of Device objects
```

#### Clip

```python
clip = track.clips[0]

# Properties
clip.name           # str - clip name
clip.length         # float - length in beats

# Actions
clip.play()         # trigger/fire the clip
```

#### Device

```python
device = track.devices[0]

# Properties
device.name         # str - device name

# Collections
device.parameters   # list of Parameter objects
```

#### Parameter

```python
param = device.parameters[0]

# Properties
param.name          # str - parameter name
param.value         # float - current value
param.min           # float - minimum value
param.max           # float - maximum value

# Set value
param.value = 0.75
```

#### Group

```python
# Groups contain multiple tracks
group = set.groups[0]  # if groups exist
```

### Complete Example

```python
import live
import random

# Connect and scan the Live set
set = live.Set(scan=True)

# Set tempo
set.tempo = 110.0

# Access first track
track = set.tracks[0]
print("Track name: %s" % track.name)

# Play first clip
clip = track.clips[0]
if clip is not None:
    clip.play()

# Randomize a device parameter
device = track.devices[0]
parameter = random.choice(device.parameters)
parameter.value = random.uniform(parameter.min, parameter.max)
print("Set %s to %s" % (parameter.name, parameter.value))
```

### Key Limitations

- **Not for MIDI notes**: pylive cannot send MIDI note events or CC messages. Use `mido` or `rtmidi` for that.
- **Requires AbletonOSC**: Must have AbletonOSC installed and running in Live.
- **Properties use @property**: Getters/setters automatically sync with Live (accessing `set.tempo` queries Live in real-time unless caching is enabled).

---

## ableton-liveapi-tools

### What It Is

A comprehensive Python Remote Script for Ableton Live that exposes 220 LiveAPI tools via a simple TCP socket interface. It provides the most extensive programmatic control available, covering playback, recording, tracks, clips, devices, MIDI notes, and Max for Live/CV Tools devices.

- **Repository**: https://github.com/Ziforge/ableton-liveapi-tools
- **License**: GPL-3.0
- **Requirements**: Ableton Live 11 or 12, Python 2.7+ (included with Live)

### Architecture

Thread-safe queue-based design:

```
┌──────────────┐    TCP (JSON)    ┌──────────────────────┐
│ Python Client│ ──────────────> │ ClaudeMCP Remote     │
│ (any app)    │   port 9004     │ Script (inside Live)  │
│              │ <────────────── │                       │
└──────────────┘                 └──────────────────────┘
```

1. Socket thread receives TCP commands on port 9004
2. Commands enter a processing queue
3. Main Ableton thread executes commands via `update_display()` callback
4. Results return through response queue to client

All LiveAPI calls execute safely on Ableton's main thread, preventing crashes.

### Installation

```bash
git clone https://github.com/Ziforge/ableton-liveapi-tools.git
cd ableton-liveapi-tools
bash install.sh
# Restart Ableton Live
python3 examples/test_connection.py
```

Manual: Copy `ClaudeMCP_Remote` folder to Ableton's Remote Scripts directory.

### Communication Protocol

**Request (JSON over TCP, newline-terminated):**
```json
{"action": "set_tempo", "bpm": 128}
```

**Response:**
```json
{"ok": true, "bpm": 128.0}
```

### The 220 Tools (44 Categories)

| Category | Count | Examples |
|----------|-------|---------|
| Session Control | 14 | playback, tempo, time signature, loop |
| Track Management | 13 | create, delete, volume, pan, solo, mute, arm, color |
| Clip Operations | 8 | create, launch, stop, duplicate |
| Clip Extras | 10 | looping, markers, gain, pitch |
| MIDI Notes | 7 | add, retrieve, remove, select |
| Device Control | 12 | parameters, presets, randomization |
| Scene Management | 6 | create, delete, fire |
| Automation | 6 | envelope manipulation |
| Routing | 8 | input/output routing |
| Browser | 4 | search, load presets |
| Transport | 8 | play, stop, record, loop |
| Groove/Quantize | 5 | quantization settings |
| Monitoring | 4 | meter levels |
| Take Lanes | 8 | Live 12+ features |
| Application Info | 4 | Live 12+ info |
| Max for Live | 5 | M4L device control |
| + 24 more | ... | ... |

### Code Examples

**Basic Control:**
```python
import socket
import json

def send_command(action, **params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 9004))
    msg = json.dumps({'action': action, **params}) + '\n'
    sock.sendall(msg.encode('utf-8'))
    response = sock.recv(4096)
    sock.close()
    return json.loads(response.decode('utf-8'))

# Set tempo
result = send_command('set_tempo', bpm=128)

# Create MIDI track
track = send_command('create_midi_track', name='Bass')
track_idx = track['track_index']

# Create clip with MIDI notes
send_command('create_midi_clip',
    track_index=track_idx,
    scene_index=0,
    length=4.0)

notes = [
    {"pitch": 36, "start": 0.0, "duration": 0.5, "velocity": 100},
    {"pitch": 38, "start": 1.0, "duration": 0.5, "velocity": 90},
    {"pitch": 36, "start": 2.0, "duration": 0.5, "velocity": 100},
    {"pitch": 42, "start": 3.0, "duration": 0.25, "velocity": 80},
]
send_command('add_notes',
    track_index=track_idx,
    scene_index=0,
    notes=notes)

# Launch clip
send_command('launch_clip',
    track_index=track_idx,
    scene_index=0)
```

**Max for Live Device Control:**
```python
# Get M4L devices on a track
devices = send_command('get_m4l_devices', track_index=0)

# Control CV LFO Rate by parameter name
send_command('set_device_param_by_name',
    track_index=0,
    device_index=2,
    param_name='Rate',
    value=0.75)
```

**Session Analysis:**
```python
# Get session info
info = send_command('get_session_info')
print(f"Tempo: {info['tempo']}")
print(f"Tracks: {info['num_tracks']}")

# Get all track names
tracks = send_command('get_track_names')
for t in tracks['tracks']:
    print(f"  {t['index']}: {t['name']}")
```

---

## Other Python Libraries

### python-osc (Low-level OSC)

Direct OSC communication with AbletonOSC:

```bash
pip install python-osc
```

```python
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 11000)
client.send_message("/live/song/set/tempo", [140])
client.send_message("/live/song/start_playing", [])
client.send_message("/live/clip_slot/create_clip", (0, 0, 4))
client.send_message("/live/clip/fire", (0, 0))
```

### python-rtmidi (MIDI)

For sending MIDI notes/CC to Ableton via virtual MIDI ports:

```bash
pip install python-rtmidi
```

See `04-midi-control.md` for details.

### mido (Higher-level MIDI)

```bash
pip install mido python-rtmidi
```

See `04-midi-control.md` for details.

## Comparison

| Feature | pylive | ableton-liveapi-tools | python-osc (raw) | rtmidi/mido |
|---------|--------|----------------------|-------------------|-------------|
| Protocol | OSC | TCP/JSON | OSC | MIDI |
| API Level | High-level | Mid-level | Low-level | Low-level |
| Tools/Methods | ~50 | 220 | Unlimited (raw OSC) | N/A |
| MIDI Notes | No | Yes | No | Yes |
| M4L Support | No | Yes | No | No |
| Dependencies | AbletonOSC | Remote Script | AbletonOSC | Virtual MIDI port |
| Pythonic API | Yes (@property) | JSON commands | Manual messages | Manual messages |
| Live Version | 11+ | 11, 12 | 11+ | Any |

## Links

- **pylive**: https://github.com/ideoforms/pylive | https://pypi.org/project/pylive/
- **ableton-liveapi-tools**: https://github.com/Ziforge/ableton-liveapi-tools
- **python-osc**: https://pypi.org/project/python-osc/
- **python-rtmidi**: https://pypi.org/project/python-rtmidi/
- **mido**: https://mido.readthedocs.io/
- **Blog - Controlling Ableton with Python**: https://sangarshanan.com/2025/02/25/connecting-python-with-ableton/
