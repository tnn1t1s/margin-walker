# Max for Live & Node for Max Integration

## What It Is

Max for Live (M4L) is the integration of Cycling '74's Max/MSP visual programming environment directly within Ableton Live. It provides the deepest level of access to Live's internals through the Live Object Model (LOM), and allows building custom instruments, effects, and control devices using visual patching, JavaScript, and Node.js.

**Node for Max (N4M)** extends this further by allowing you to run Node.js processes from within Max patches, enabling access to npm packages, web servers, file systems, and external APIs -- all from within a Max for Live device.

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Ableton Live                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │  Max for Live Device                          │  │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────────┐  │  │
│  │  │  Max     │  │  js      │  │ node.script  │  │  │
│  │  │  Patcher │  │  object  │  │  object      │  │  │
│  │  │  (visual)│  │(LiveAPI) │  │  (Node.js)   │  │  │
│  │  └────┬────┘  └────┬─────┘  └──────┬──────┘  │  │
│  │       │            │               │          │  │
│  │       ▼            ▼               ▼          │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  Live Object Model (LOM)                │  │  │
│  │  │  (Song, Track, Clip, Device, etc.)      │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Three Programming Approaches in M4L

1. **Visual Patching** -- Standard Max objects connected via patch cables
2. **JavaScript (js object)** -- Full LiveAPI access via the `LiveAPI` JavaScript class
3. **Node.js (node.script)** -- Run Node.js processes, but **cannot directly access LiveAPI** (must communicate with a `js` object for LOM access)

## Installation / Setup

### Max for Live
- Included with **Ableton Live Suite** (no separate installation)
- Available as an add-on for **Ableton Live Standard**
- Not available for Ableton Live Intro

### Node for Max
- Included with Max 8+ and Max for Live
- Uses Node v20.6.1 and npm v9.8.1 (bundled)
- No separate installation required

### Creating a Max for Live Device

1. In Ableton Live, drag a "Max Audio Effect", "Max Instrument", or "Max MIDI Effect" into a track
2. Click the device title bar wrench icon to open the Max editor
3. Build your device using Max objects, JavaScript, or Node.js
4. Save as `.amxd` file

## JavaScript LiveAPI (js object)

The `js` object in Max allows you to write JavaScript that accesses the Live Object Model directly.

### LiveAPI Constructor

```javascript
// Create LiveAPI with callback and path
var api = new LiveAPI(callback, "live_set");

// Or with specific path
var api = new LiveAPI(callback, "live_set tracks 0");

// Or with object ID
var api = new LiveAPI(callback, id);
```

**Important**: You cannot use LiveAPI in JavaScript global code. Use `live.thisdevice` to detect when your device finishes loading.

### LiveAPI Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `id` | String | Get | Dynamic identifier for referenced Live object |
| `path` | String | Get | Stable path (e.g., "live_set tracks 0 devices 0") |
| `unquotedpath` | String | Get | Unquoted version of path |
| `children` | Array | Get | Array of child object types |
| `mode` | Number | Get/Set | 0=follows object, 1=follows UI location |
| `type` | String | Get | Object type at current path |
| `info` | String | Get | Full description (id, type, children, properties, functions) |
| `property` | String | Get/Set | Observed property for change notifications |
| `proptype` | String | Get | Type of observed property |

### LiveAPI Methods

```javascript
// Navigate to a path
api.goto("live_set tracks 0");

// Get a property value
var tempo = api.get("tempo");
var trackName = api.get("name");

// Get property as string
var name = api.getstring("name");

// Set a property
api.set("tempo", 128.0);
api.set("name", "Bass");
api.set("mute", 1);

// Call a function
api.call("fire");           // Fire a clip
api.call("stop");           // Stop a clip
api.call("start_playing");  // Start transport

// Get child count
var numTracks = api.getcount("tracks");
var numDevices = api.getcount("devices");
```

### Complete JavaScript Example

```javascript
// File: my_device.js (loaded via [js my_device.js] object in Max)

var song_api;
var track_api;

function bang() {
    // Initialize LiveAPI objects
    song_api = new LiveAPI(song_callback, "live_set");
    track_api = new LiveAPI(track_callback, "live_set tracks 0");

    // Get song info
    var tempo = song_api.get("tempo");
    var numTracks = song_api.getcount("tracks");
    post("Tempo:", tempo, "Tracks:", numTracks, "\n");

    // Set up property observation
    song_api.property = "tempo";

    // Get track info
    var trackName = track_api.get("name");
    var isMuted = track_api.get("mute");
    post("Track:", trackName, "Muted:", isMuted, "\n");

    // Control transport
    song_api.call("start_playing");

    // Navigate track devices
    var numDevices = track_api.getcount("devices");
    for (var i = 0; i < numDevices; i++) {
        var device_api = new LiveAPI(null, "live_set tracks 0 devices " + i);
        post("Device:", device_api.get("name"), "\n");

        // Get device parameters
        var numParams = device_api.getcount("parameters");
        for (var j = 0; j < numParams; j++) {
            var param_api = new LiveAPI(null,
                "live_set tracks 0 devices " + i + " parameters " + j);
            post("  Param:", param_api.get("name"),
                 "Value:", param_api.get("value"), "\n");
        }
    }
}

function song_callback(args) {
    post("Song changed:", args, "\n");
    // args[0] = property name, args[1] = new value
}

function track_callback(args) {
    post("Track changed:", args, "\n");
}

// Receive messages from Max patcher
function set_tempo(val) {
    song_api.set("tempo", val);
}

function set_track_mute(track_idx, mute_state) {
    var api = new LiveAPI(null, "live_set tracks " + track_idx);
    api.set("mute", mute_state);
}
```

### Scheduler Constraint

LiveAPI **cannot be created or used** in Max's high-priority thread. Use `defer` or `deferlow` objects to requeue messages to the `js` object from high-priority contexts (like audio rate signals).

## Node for Max (node.script)

### Overview

Node for Max lets you run Node.js applications from within Max patches using the `node.script` object. Key features:

- Each `node.script` runs an isolated Node process
- Access to npm packages and the full Node.js ecosystem
- Communication with Max via the `max-api` module
- Cannot directly access LiveAPI (must bridge through a `js` object)

### Basic Node for Max Setup

**Max Patcher:**
```
[node.script my_node_app.js]
```

**Node.js Script (my_node_app.js):**
```javascript
const maxApi = require("max-api");

// Receive messages from Max
maxApi.addHandler("tempo", (value) => {
    maxApi.post(`Received tempo: ${value}`);
    // Process and send back
    maxApi.outlet(value * 2);
});

// Send messages to Max outlet
maxApi.outlet("hello", "from", "node");

// Post to Max console
maxApi.post("Node script started");

// Dictionary support
maxApi.addHandler("dict", async (dictId) => {
    const dict = await maxApi.getDict(dictId);
    maxApi.post(JSON.stringify(dict));
});
```

### max-api Module Methods

```javascript
const maxApi = require("max-api");

// Output to Max patcher
maxApi.outlet(...args);           // Send to left outlet
maxApi.outletBang();              // Send bang

// Receive from Max
maxApi.addHandler("name", fn);    // Named message handler
maxApi.addHandler(maxApi.MESSAGE_TYPES.BANG, fn);  // Bang handler
maxApi.addHandler(maxApi.MESSAGE_TYPES.ALL, fn);   // Catch-all

// Max console
maxApi.post(...args);             // Post to console
maxApi.error(...args);            // Post error

// Dictionaries
maxApi.getDict(name);             // Get dictionary contents
maxApi.setDict(name, obj);        // Set dictionary contents
maxApi.updateDict(name, path, val); // Update specific key
```

### Bridging Node.js to LiveAPI

Since `node.script` cannot access LiveAPI directly, you bridge through a `js` object:

```
┌──────────────┐    messages    ┌──────────┐   LiveAPI   ┌──────────┐
│ node.script  │ ────────────> │ js object │ ──────────> │  Live    │
│ (Node.js)    │ <──────────── │ (LiveAPI) │ <────────── │  LOM     │
└──────────────┘               └──────────┘              └──────────┘
```

**Max Patcher Connection:**
```
[node.script server.js] → [js liveapi_bridge.js] → [live.object]
```

### Community Projects

**max4node** (https://github.com/alpacaaa/max4node):
- Exposes the Live Object Model via UDP sockets to Node.js
- Allows controlling Ableton from an external Node.js application
- Communicates through a Max for Live device using UDP

**m4l_js2liveAPI** (https://github.com/blm81/m4l_js2liveAPI):
- JavaScript classes that interface with Ableton Live API
- Designed for use within Max for Live js objects

## Node for Max Documentation

Full documentation: https://docs.cycling74.com/max8/vignettes/00_N4M_index

Covers 12 major topics:
1. Anatomy of N4M patches
2. npm integration and package management
3. Projects and Max for Live device compatibility
4. Differences between `js` and `node.script` objects
5. Process lifecycle management
6. Debugging with `node.debug`
7. The max-api module and JavaScript API
8. Node.script lifecycle events
9. Custom Node/npm binary configuration
10. Remote debugging
11. Standard I/O handling
12. ECMAScript module support

## Key Limitations

- **LiveAPI not available in node.script**: Must bridge through a `js` object
- **Scheduler constraints**: LiveAPI cannot run in Max's high-priority thread
- **M4L device required**: All M4L code must run within an `.amxd` device loaded in a track
- **Live Suite required**: M4L is only included with Live Suite (or as a paid add-on for Standard)
- **Single Node process per node.script**: Each object manages one isolated process

## Links

- **Max for Live overview**: https://www.ableton.com/en/live/max-for-live/
- **Controlling Live with M4L**: https://help.ableton.com/hc/en-us/articles/5402681764242
- **LiveAPI JS reference**: https://docs.cycling74.com/max8/vignettes/jsliveapi
- **Node for Max docs**: https://docs.cycling74.com/max8/vignettes/00_N4M_index
- **Node for Max API**: https://docs.cycling74.com/nodeformax/api/
- **Live Object Model**: https://docs.cycling74.com/max8/vignettes/live_object_model
- **Max Cookbook - Live API via JS**: https://music.arts.uci.edu/dobrian/maxcookbook/live-api-javascript
- **max4node**: https://github.com/alpacaaa/max4node
