# Ableton Live Remote Script API (Python)

## What It Is

Ableton Live's Remote Script API is an internal Python-based system that allows programmatic control of Ableton Live through MIDI Remote Scripts. These scripts are Python programs that configure remote control surfaces directly with Live, providing bidirectional communication between external controllers/software and Live's internal state.

The API exposes the **Live Object Model (LOM)** -- the complete hierarchy of objects representing a Live session (Song, Track, Clip, Device, Parameter, etc.).

## How It Works

### Architecture

- Remote Scripts are Python modules placed in Ableton's Remote Scripts directory
- Live loads and executes them in its embedded Python interpreter (CPython)
- Scripts run on Ableton's main thread via the `update_display()` callback loop
- They can read/write any property exposed by the Live Object Model
- Communication is bidirectional: scripts can both query state and receive change notifications

### File Structure

Scripts are located at:
- **macOS**: `/Applications/Ableton Live.app/Contents/App-Resources/MIDI Remote Scripts/`
- **Windows**: `C:\Program Files\Ableton\Live\Resources\MIDI Remote Scripts`

Each controller has a dedicated folder containing `.py` source files and `.pyc` compiled bytecode.

### Live Object Model (LOM) Hierarchy

```
Application
  └── Song (Live Set)
       ├── tracks[] (Track)
       │    ├── clip_slots[] (ClipSlot)
       │    │    └── clip (Clip)
       │    ├── devices[] (Device)
       │    │    └── parameters[] (DeviceParameter)
       │    ├── mixer_device (MixerDevice)
       │    └── view (Track.View)
       ├── return_tracks[] (Track)
       ├── master_track (Track)
       ├── scenes[] (Scene)
       ├── cue_points[] (CuePoint)
       └── view (Song.View)
```

## Installation / Setup

### Creating a Custom Remote Script

1. Navigate to the Remote Scripts directory (see paths above)
2. Create a new folder with your script name (e.g., `MyScript`)
3. Create `__init__.py` with a `create_instance()` function:

```python
from .MyScript import MyScript

def create_instance(c_instance):
    return MyScript(c_instance)
```

4. Create your main script class inheriting from `ControlSurface`:

```python
from _Framework.ControlSurface import ControlSurface

class MyScript(ControlSurface):
    def __init__(self, c_instance):
        super(MyScript, self).__init__(c_instance)
        with self.component_guard():
            self._setup()

    def _setup(self):
        self.song().add_tempo_listener(self._on_tempo_changed)

    def _on_tempo_changed(self):
        self.log_message("Tempo: %s" % self.song().tempo)

    def update_display(self):
        # Called ~10 times per second by Live
        super(MyScript, self).update_display()

    def disconnect(self):
        self.song().remove_tempo_listener(self._on_tempo_changed)
        super(MyScript, self).disconnect()
```

5. Restart Ableton Live
6. Select the script in Preferences > Link/Tempo/MIDI > Control Surface

### Installing Third-Party Scripts

1. Download the script package
2. Copy to `~/Music/Ableton/User Library/Remote Scripts/` (macOS) or `\Users\[username]\Documents\Ableton\User Library\Remote Scripts` (Windows)
3. Restart Live
4. Select in Preferences > Link/Tempo/MIDI

## Key API Classes and Methods

### Song (Live Set)

```python
song = self.song()

# Transport
song.is_playing          # bool - playback state
song.tempo               # float - BPM
song.current_song_time   # float - current position in beats
song.loop                # bool - loop enabled
song.loop_start          # float - loop start in beats
song.loop_length         # float - loop length in beats
song.record_mode         # bool - recording state
song.metronome           # bool - metronome on/off

# Actions
song.start_playing()
song.stop_playing()
song.continue_playing()
song.undo()
song.redo()
song.create_midi_track(index)
song.create_audio_track(index)
song.create_return_track()
song.create_scene(index)
song.duplicate_scene(index)
song.delete_scene(index)

# Collections
song.tracks              # tuple of Track objects
song.return_tracks       # tuple of return Track objects
song.master_track        # Track object
song.scenes              # tuple of Scene objects
song.visible_tracks      # tuple of visible Track objects
```

### Track

```python
track = song.tracks[0]

track.name               # str
track.color               # int (color value)
track.arm                # bool - record arm
track.mute               # bool
track.solo               # bool
track.volume             # via mixer_device
track.panning            # via mixer_device
track.has_midi_input     # bool
track.has_audio_input    # bool
track.is_grouped         # bool
track.is_foldable        # bool
track.clip_slots         # tuple of ClipSlot
track.devices            # tuple of Device
track.mixer_device       # MixerDevice

track.stop_all_clips()
```

### Clip

```python
clip = track.clip_slots[0].clip

clip.name                # str
clip.length              # float - length in beats
clip.is_playing          # bool
clip.is_recording        # bool
clip.looping             # bool
clip.loop_start          # float
clip.loop_end            # float
clip.start_marker        # float
clip.end_marker          # float

clip.fire()              # trigger clip
clip.stop()
clip.duplicate_loop()

# MIDI operations (MIDI clips only)
clip.get_notes(start, start_pitch, length, pitch_span)
clip.set_notes(notes)    # notes is a tuple of (pitch, time, duration, velocity, mute)
clip.remove_notes(start, start_pitch, length, pitch_span)
```

### Device & Parameters

```python
device = track.devices[0]

device.name              # str
device.type              # DeviceType enum
device.parameters        # tuple of DeviceParameter

param = device.parameters[0]
param.name               # str
param.value              # float
param.min                # float
param.max                # float
param.is_quantized       # bool
```

### Listeners

Most properties support listener callbacks for change notifications:

```python
# Add listener
song.add_tempo_listener(callback_function)
track.add_mute_listener(callback_function)
clip.add_playing_status_listener(callback_function)

# Remove listener
song.remove_tempo_listener(callback_function)
```

## Notable Projects Using the Remote Script API

### ableton-liveapi-tools (Ziforge)
- **URL**: https://github.com/Ziforge/ableton-liveapi-tools
- Exposes 220 LiveAPI tools via TCP socket (port 9004)
- Thread-safe queue-based design
- JSON command/response protocol
- Supports Live 11 and 12

### Decompiled Script References
- **Live 11**: https://github.com/gluon/AbletonLive11_MIDIRemoteScripts
- **Structure Void docs**: https://structure-void.com/ableton-live-midi-remote-scripts/
- API documentation available for Live versions 9.2 through 12.0.1

## API Documentation Sources

- Live Object Model (LOM): https://docs.cycling74.com/max8/vignettes/live_object_model
- Structure Void Python API reference: https://structure-void.com/ableton-live-midi-remote-scripts/
- Decompiled _Framework source in Live's installation directory
- Cycling '74 Max documentation for LOM paths and object properties

## Key Limitations

- No official public documentation from Ableton (the API is technically internal/unsupported)
- Scripts must run inside Live's Python environment (embedded CPython)
- All LiveAPI calls must happen on the main thread
- The Python version is dictated by the Live version (typically Python 3.x in Live 11+)
- Cannot directly import external packages unless they are pure Python and placed alongside the script
