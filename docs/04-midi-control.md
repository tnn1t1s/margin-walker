# Programmatic MIDI Control of Ableton Live

## What It Is

MIDI (Musical Instrument Digital Interface) is the most basic and universal protocol for controlling Ableton Live programmatically. By sending MIDI messages from an external script (Python, Node.js, etc.) through virtual MIDI ports, you can trigger notes, control parameters via CC messages, and automate clip launching without any special Ableton plugins or remote scripts.

## How It Works

### Architecture

```
┌─────────────────┐     Virtual MIDI      ┌───────────────────┐
│  Python/Node.js │ ───────────────────>  │  Ableton Live     │
│  Script         │     (IAC Driver /     │  (MIDI Track or   │
│  (rtmidi, mido) │      loopMIDI)        │   MIDI Map)       │
└─────────────────┘                       └───────────────────┘
```

1. **External script** generates MIDI messages (Note On/Off, CC, Program Change, etc.)
2. **Virtual MIDI driver** creates a software MIDI port visible to both the script and Ableton
3. **Ableton Live** receives messages on a MIDI track input or via MIDI mapping

### Virtual MIDI Port Setup

**macOS (IAC Driver -- built in, no install needed):**
1. Open Audio MIDI Setup from `/Applications/Utilities/`
2. Navigate to `Window` > `Show MIDI Studio`
3. Double-click the IAC Driver icon
4. Check "Device is Online"
5. Use the `+` button to create virtual MIDI buses (e.g., "Bus 1", "Bus 2")
6. Each bus can carry 16 MIDI channels

**Windows (loopMIDI -- third-party, free):**
1. Download loopMIDI from Tobias Erichsen's site: https://www.tobias-erichsen.de/software/loopmidi.html
2. Install and run
3. Create virtual MIDI ports with the `+` button
4. Ports appear in Ableton's MIDI preferences

**Linux (ALSA virtual MIDI):**
```bash
sudo modprobe snd-virmidi
# Creates virtual MIDI ports accessible via ALSA
```

### Ableton MIDI Configuration

1. Open Preferences (Ctrl/Cmd + ,)
2. Go to Link/Tempo/MIDI tab
3. Under MIDI Ports, find your virtual MIDI port
4. Enable "Track" for input (to receive notes on MIDI tracks)
5. Enable "Remote" for input (to receive MIDI-mapped controls)
6. Set MIDI track input to the virtual port and desired channel

## Python Libraries

### python-rtmidi (recommended)

The most direct library for sending MIDI from Python.

**Installation:**
```bash
pip install python-rtmidi
```

**Sending MIDI Notes:**
```python
import time
import rtmidi

# Create MIDI output
midi_out = rtmidi.MidiOut()

# List available ports
available_ports = midi_out.get_ports()
print("Available MIDI ports:", available_ports)

# Open port (0 = first available, usually IAC Driver Bus 1)
midi_out.open_port(0)

# MIDI message format: [status_byte, data1, data2]
# Status bytes:
#   0x90 = Note On (channel 1)
#   0x80 = Note Off (channel 1)
#   0x91 = Note On (channel 2)
#   0xB0 = Control Change (channel 1)

def send_note(pitch, velocity=100, duration=0.5, channel=0):
    """Send a MIDI note with given pitch, velocity, and duration."""
    note_on = [0x90 + channel, pitch, velocity]
    note_off = [0x80 + channel, pitch, 0]
    midi_out.send_message(note_on)
    time.sleep(duration)
    midi_out.send_message(note_off)

def send_cc(cc_number, value, channel=0):
    """Send a MIDI Control Change message."""
    cc_msg = [0xB0 + channel, cc_number, value]
    midi_out.send_message(cc_msg)

def send_program_change(program, channel=0):
    """Send a MIDI Program Change message."""
    pc_msg = [0xC0 + channel, program]
    midi_out.send_message(pc_msg)

# Play a C major chord
for note in [60, 64, 67]:  # C4, E4, G4
    midi_out.send_message([0x90, note, 100])
time.sleep(1.0)
for note in [60, 64, 67]:
    midi_out.send_message([0x80, note, 0])

# Send CC to control a parameter (e.g., filter cutoff)
send_cc(74, 64)  # CC#74 = brightness/cutoff, value 64 (midpoint)

# Clean up
midi_out.close_port()
del midi_out
```

**Receiving MIDI (from Ableton):**
```python
import rtmidi

midi_in = rtmidi.MidiIn()
midi_in.open_port(0)

# Polling approach
while True:
    msg = midi_in.get_message()
    if msg:
        message, delta_time = msg
        print(f"Message: {message}, Delta: {delta_time}")

# Callback approach
def callback(message, data):
    msg, delta = message
    print(f"Received: {msg}")

midi_in.set_callback(callback)
```

### mido (higher-level MIDI library)

**Installation:**
```bash
pip install mido python-rtmidi
```

**Usage:**
```python
import mido

# List ports
print(mido.get_output_names())
print(mido.get_input_names())

# Open output port
port = mido.open_output('IAC Driver Bus 1')

# Send messages using mido's message objects
port.send(mido.Message('note_on', note=60, velocity=100, channel=0))
port.send(mido.Message('note_off', note=60, velocity=0, channel=0))
port.send(mido.Message('control_change', control=74, value=64, channel=0))
port.send(mido.Message('program_change', program=5, channel=0))
port.send(mido.Message('pitchwheel', pitch=0, channel=0))

# Create and save MIDI files
mid = mido.MidiFile()
track = mido.MidiTrack()
mid.tracks.append(track)

track.append(mido.Message('note_on', note=60, velocity=100, time=0))
track.append(mido.Message('note_off', note=60, velocity=0, time=480))
track.append(mido.Message('note_on', note=64, velocity=100, time=0))
track.append(mido.Message('note_off', note=64, velocity=0, time=480))

mid.save('output.mid')
```

## Node.js Libraries

### easymidi

```bash
npm install easymidi
```

```javascript
const easymidi = require('easymidi');

// List available ports
console.log(easymidi.getOutputs());

// Open output
const output = new easymidi.Output('IAC Driver Bus 1');

// Send note
output.send('noteon', { note: 60, velocity: 100, channel: 0 });
setTimeout(() => {
    output.send('noteoff', { note: 60, velocity: 0, channel: 0 });
}, 500);

// Send CC
output.send('cc', { controller: 74, value: 64, channel: 0 });
```

### midi (Web MIDI API in browser)

```javascript
// Browser-based Web MIDI API
navigator.requestMIDIAccess().then(access => {
    const outputs = access.outputs;
    outputs.forEach(output => {
        // Note On: channel 1, note 60, velocity 100
        output.send([0x90, 60, 100]);
        // Note Off after 500ms
        output.send([0x80, 60, 0], performance.now() + 500);
    });
});
```

## MIDI Message Reference

### Status Bytes

| Message | Status Byte | Data 1 | Data 2 |
|---------|------------|--------|--------|
| Note Off | 0x80 + channel | Note (0-127) | Velocity (0-127) |
| Note On | 0x90 + channel | Note (0-127) | Velocity (1-127) |
| Poly Aftertouch | 0xA0 + channel | Note | Pressure |
| Control Change | 0xB0 + channel | CC# (0-127) | Value (0-127) |
| Program Change | 0xC0 + channel | Program (0-127) | -- |
| Channel Aftertouch | 0xD0 + channel | Pressure | -- |
| Pitch Bend | 0xE0 + channel | LSB (0-127) | MSB (0-127) |

### Common CC Numbers for Ableton

| CC# | Common Use |
|-----|-----------|
| 1 | Modulation wheel |
| 7 | Volume |
| 10 | Pan |
| 11 | Expression |
| 64 | Sustain pedal |
| 71 | Resonance |
| 74 | Frequency / Cutoff |

### MIDI Mapping in Ableton

1. Enter MIDI Map Mode (Cmd/Ctrl + M)
2. Click the parameter you want to map
3. Send a MIDI CC message from your script
4. The parameter is now mapped to that CC
5. Exit MIDI Map Mode

This allows CC messages from your script to control any mappable parameter in Live (mixer, effects, instruments, etc.).

## Advanced: Clip Launching via MIDI

Ableton can receive MIDI notes to trigger clips in Session View when configured:

1. Set a MIDI track to receive from your virtual port
2. Use MIDI mapping to assign specific notes to clip slots
3. Or use a dedicated control surface script that maps notes to clip launches

## Comparison with Other Methods

| Feature | MIDI | OSC (AbletonOSC) | Remote Script |
|---------|------|-------------------|---------------|
| Setup complexity | Low | Medium | High |
| Control granularity | Limited (notes, CC) | Full LOM access | Full LOM access |
| Bidirectional | Limited | Yes | Yes |
| Requires plugin | No | Yes (Remote Script) | Yes |
| Latency | Low | Low | Lowest |
| Note input | Yes | No | Yes |
| Parameter names | No (CC numbers) | Yes | Yes |

## Links

- **python-rtmidi**: https://pypi.org/project/python-rtmidi/
- **mido**: https://mido.readthedocs.io/
- **loopMIDI (Windows)**: https://www.tobias-erichsen.de/software/loopmidi.html
- **Tutorial - Python MIDI to Ableton**: https://aleksati.net/posts/using-python-to-control-ableton-live-with-midi
- **Tutorial - Gorilla Sun**: https://www.gorillasun.de/blog/sending-midi-signals-from-python-to-ableton-live-2023/
- **GitHub tutorial repo**: https://github.com/AhmadMoussa/Python-Midi-Ableton
