# ableton-js - Node.js Library for Ableton Live Control

## What It Is

ableton-js is a TypeScript/Node.js library that provides programmatic control of Ableton Live through a MIDI Remote Script. It exposes Ableton's MIDI Remote Script functions to TypeScript, covering extensive functionality including transport control, track manipulation, clip management, device parameter control, and real-time event listeners.

- **npm**: https://www.npmjs.com/package/ableton-js
- **Repository**: https://github.com/leolabs/ableton-js
- **Latest version**: 4.0.3
- **License**: MIT
- **Author**: Leo Bernard (leolabs)

## How It Works

### Protocol / Architecture

```
┌─────────────────┐     UDP (JSON)      ┌───────────────────┐
│  Node.js App    │ ──────────────────> │  AbletonJS MIDI   │
│  (ableton-js)   │                     │  Remote Script     │
│                 │ <────────────────── │  (inside Live)     │
│  TypeScript     │     UDP (JSON)      │                    │
└─────────────────┘                     └───────────────────┘
```

- **Communication**: UDP-based JSON messaging with UUID association
- **Port discovery**: Both client and server bind random ports, stored locally for discovery
- **Compression**: Messages are gzip-compressed and chunked to fit UDP packet limits
- **Chunking**: First byte contains chunk index (0x00-0xFF), 0xFF indicates final chunk requiring reassembly
- **Caching**: Properties generate MD5 eTags for client-side LRU caching; matching eTags return placeholder objects

### Message Format

**Request:**
```json
{
  "uuid": "unique-id",
  "ns": "song",
  "nsid": null,
  "name": "get_tempo",
  "args": {},
  "etag": "cached-md5-hash",
  "cache": true
}
```

**Response:**
```json
{
  "uuid": "unique-id",
  "event": "result",
  "data": 120.0
}
```

## Installation / Setup

### 1. Install the npm package

```bash
npm install ableton-js
```

### 2. Install the MIDI Remote Script in Ableton

1. Locate the `midi-script` folder from the ableton-js package (in `node_modules/ableton-js/midi-script`)
2. Copy it to Ableton's Remote Scripts folder:
   - **macOS**: `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows**: `\Users\[username]\Documents\Ableton\User Library\Remote Scripts`
3. Rename the folder to `AbletonJS`
4. Launch Ableton Live
5. Go to Settings > Link, Tempo & MIDI
6. Select "AbletonJS" from the Control Surface dropdown
7. Set Input/Output to "None"

**macOS shortcut** (if using yarn):
```bash
yarn ableton10:start   # For Live 10
yarn ableton11:start   # For Live 11
```

## Key API Methods

### Connection & Lifecycle

```typescript
import { Ableton } from "ableton-js";

const ableton = new Ableton({ logger: console });

// Start connection
await ableton.start();

// Event handlers
ableton.on("connect", () => console.log("Connected to Ableton"));
ableton.on("disconnect", () => console.log("Disconnected"));
ableton.on("error", (e) => console.error("Error:", e));
ableton.on("ping", (ms) => console.log("Ping:", ms, "ms"));
ableton.on("message", (m) => console.log("Message:", m));
```

### Song (Transport & Global)

```typescript
// Get properties
const tempo = await ableton.song.get("tempo");
const isPlaying = await ableton.song.get("is_playing");
const songTime = await ableton.song.get("current_song_time");

// Set properties
await ableton.song.set("tempo", 128);
await ableton.song.set("metronome", true);
await ableton.song.set("loop", true);
await ableton.song.set("loop_start", 0);
await ableton.song.set("loop_length", 16);

// Transport control
await ableton.song.startPlaying();
await ableton.song.stopPlaying();
await ableton.song.continuePlaying();

// Session operations
await ableton.song.createMidiTrack();
await ableton.song.createAudioTrack();
await ableton.song.createReturnTrack();
await ableton.song.createScene();
await ableton.song.undo();
await ableton.song.redo();
```

### Event Listeners

```typescript
// Listen for property changes
ableton.song.addListener("is_playing", (playing) => {
    console.log("Playing:", playing);
});

ableton.song.addListener("tempo", (tempo) => {
    console.log("Tempo changed:", tempo);
});

// Track listeners
const tracks = await ableton.song.get("tracks");
const track = tracks[0];

track.addListener("mute", (muted) => {
    console.log("Track mute:", muted);
});

track.addListener("volume", (vol) => {
    console.log("Volume:", vol);
});
```

**Note**: Listeners can fire 20-30 updates per second. When opening new Ableton projects, the script disconnects and reconnects -- listeners are automatically cleared. Reattach listeners on each `connect` event.

### Tracks

```typescript
// Get all tracks
const tracks = await ableton.song.get("tracks");

for (const track of tracks) {
    const name = await track.get("name");
    const muted = await track.get("mute");
    const armed = await track.get("arm");
    console.log(`${name}: muted=${muted}, armed=${armed}`);
}

// Modify track properties
const track = tracks[0];
await track.set("name", "Bass");
await track.set("mute", false);
await track.set("solo", true);
await track.set("arm", true);
await track.set("volume", 0.85);
await track.set("panning", 0.0);

// Stop clips on track
await track.stopAllClips();
```

### Clips

```typescript
// Get clip slots
const clipSlots = await track.get("clip_slots");
const clipSlot = clipSlots[0];

// Check if clip exists
const hasClip = await clipSlot.get("has_clip");

if (hasClip) {
    const clip = await clipSlot.get("clip");
    const clipName = await clip.get("name");
    const length = await clip.get("length");

    // Fire/stop clip
    await clip.fire();
    await clip.stop();

    // Modify clip properties
    await clip.set("name", "Intro Pattern");
    await clip.set("looping", true);
    await clip.set("loop_start", 0);
    await clip.set("loop_end", 4.0);
}
```

### Devices & Parameters

```typescript
// Get devices on a track
const devices = await track.get("devices");

for (const device of devices) {
    const deviceName = await device.get("name");
    const params = await device.get("parameters");

    console.log(`Device: ${deviceName}`);

    for (const param of params) {
        const paramName = await param.get("name");
        const value = await param.get("value");
        const min = await param.get("min");
        const max = await param.get("max");
        console.log(`  ${paramName}: ${value} (${min}-${max})`);
    }
}

// Set device parameter
const param = (await devices[0].get("parameters"))[1];
await param.set("value", 0.5);
```

### Scenes

```typescript
const scenes = await ableton.song.get("scenes");

for (const scene of scenes) {
    const name = await scene.get("name");
    console.log("Scene:", name);
}

// Fire a scene
await scenes[0].fire();
```

## Complete Example

```typescript
import { Ableton } from "ableton-js";

const ableton = new Ableton({ logger: console });

async function main() {
    await ableton.start();

    // Set up reconnection handler
    ableton.on("connect", async () => {
        console.log("Connected to Ableton Live");

        // Get song info
        const tempo = await ableton.song.get("tempo");
        console.log("Current tempo:", tempo);

        // List all tracks
        const tracks = await ableton.song.get("tracks");
        for (const track of tracks) {
            const name = await track.get("name");
            console.log("Track:", name);
        }

        // Watch for tempo changes
        ableton.song.addListener("tempo", (newTempo) => {
            console.log("Tempo changed to:", newTempo);
        });

        // Watch for play/stop
        ableton.song.addListener("is_playing", (playing) => {
            console.log(playing ? "Playing" : "Stopped");
        });
    });

    ableton.on("disconnect", () => {
        console.log("Disconnected from Ableton Live");
    });
}

main().catch(console.error);
```

## Known Limitations

- `output_meter_level` listener has performance issues; use `output_meter_left`/`output_meter_right` instead
- `playing_status` listener for clip slots doesn't fire in Ableton
- When Ableton opens a new project, the connection drops and reconnects (listeners are cleared)
- UDP packet size limits mean large responses are chunked and reassembled

## Related Projects

- **ableton-copilot-mcp**: MCP server built on ableton-js for AI assistant control -- https://github.com/xiaolaa2/ableton-copilot-mcp
- **nodeLOM**: Control Ableton from Node.js via web sockets -- https://github.com/iamjoncannon/nodeLOM

## Links

- **npm**: https://www.npmjs.com/package/ableton-js
- **GitHub**: https://github.com/leolabs/ableton-js
- **MIDI scripting Ableton with Node.js tutorial**: https://www.asepbagja.com/programming/midi-scripting-ableton-nodejs/
