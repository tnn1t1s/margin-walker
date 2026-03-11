# Ableton Link - Tempo Sync Protocol

## What It Is

Ableton Link is a technology that synchronizes musical beat, tempo, phase, and start/stop commands across multiple applications running on one or more devices. Applications on devices connected to a local network discover each other automatically and form a musical session in which each participant can perform independently while maintaining temporal alignment.

- **Repository**: https://github.com/Ableton/link
- **Documentation**: https://ableton.github.io/link/
- **iOS SDK (LinkKit)**: https://github.com/Ableton/LinkKit
- **License**: Dual-licensed under GPLv2+ and proprietary (contact link-devs@ableton.com for proprietary)
- **Latest Release**: Link 4.0.0 beta 2 (March 2026)
- **Language**: C++ (header-only library)

## How It Works

### Protocol Architecture

Link operates on a local network using peer-to-peer discovery (no central server):

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Ableton     │     │  iOS App     │     │  Custom App  │
│  Live        │◄───►│  (LinkKit)   │◄───►│  (Link SDK)  │
│              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
        ▲                    ▲                    ▲
        └────────────────────┴────────────────────┘
              Local Network (auto-discovery)
```

### Core Concepts

**Timeline Model**: A session timeline is represented as a triple of `(beat, time, tempo)` which defines a bijection between beats and time values. This is the most fundamental service Link provides -- converting between beat space and time space.

**Tempo Synchronization**: Any participant can propose tempo changes. Each participant adopts the last tempo value proposed on the network. There is no master/slave -- it works like live musicians adjusting together.

**Beat Alignment**: An integral beat value on any participant's timeline corresponds to an integral beat value on all other participants' timelines. This ensures synchronized beat positions while allowing different absolute beat counts.

**Phase Synchronization**: Applications specify a **quantum** value (in beats) for phase alignment. Link guarantees that participants with the same quantum value will be phase-aligned. For example, with quantum=4, bar boundaries will be synchronized across all participants.

**Start/Stop Synchronization** (Link v3): Shared transport state. Start/stop changes only follow user actions -- apps don't auto-adapt when joining. Upon starting, they follow their quantum and phase alignment.

### Session Management

Link uses a **capture-commit model**:
1. Capture a session state snapshot
2. Query or modify properties on the snapshot
3. Commit changes back to the session

A captured state has consistent values for the duration of a computation.

### Thread Safety

- **Audio thread**: Use realtime-safe capture/commit functions
- **Application thread**: May query but should avoid modifying state (asynchronous delays)
- **Recommendation**: Only modify Link session state from the audio thread

## Installation / Setup

### Prerequisites

- CMake build system
- Platform-specific toolchains:
  - **Windows**: MSVC 17 2022
  - **macOS**: Xcode 16.2.0
  - **Linux**: Clang 13+ or GCC 10+

### Building from Source

```bash
git clone https://github.com/Ableton/link.git
cd link
git submodule update --init --recursive

mkdir build
cd build
cmake ..
cmake --build .
```

Binaries output to `bin/` subdirectory.

### Integration into Your Project

**CMake Projects:**
```cmake
include($PATH_TO_LINK/AbletonLinkConfig.cmake)
target_link_libraries($YOUR_TARGET Ableton::Link)
```

**Non-CMake Projects:**
- Add `include/` and `modules/asio-standalone/asio/include/` to include paths
- Define platform macro: `LINK_PLATFORM_MACOSX=1`, `LINK_PLATFORM_LINUX=1`, or `LINK_PLATFORM_WINDOWS=1`

Link is **header-only** -- include either:
- `Link.hpp` for basic Link
- `LinkAudio.hpp` for Link with audio support

## Key API

### Core Classes

**`ableton::Link`** -- Main entry point

```cpp
#include <ableton/Link.hpp>

// Create Link instance with initial tempo
ableton::Link link(120.0);

// Enable/disable Link
link.enable(true);

// Check number of peers
int numPeers = link.numPeers();

// Set callback for peer count changes
link.setNumPeersCallback([](std::size_t numPeers) {
    // Handle peer count change
});

// Set callback for tempo changes
link.setTempoCallback([](double tempo) {
    // Handle tempo change from network
});

// Set callback for start/stop state changes
link.setStartStopCallback([](bool isPlaying) {
    // Handle transport state change
});
```

**`ableton::Link::SessionState`** -- Captured session state

```cpp
// In audio callback:
auto sessionState = link.captureAudioSessionState();

// Query tempo
double tempo = sessionState.tempo();

// Query beat at a given time
double beat = sessionState.beatAtTime(hostTime, quantum);

// Query phase at a given time
double phase = sessionState.phaseAtTime(hostTime, quantum);

// Set tempo
sessionState.setTempo(140.0, hostTime);

// Request beat position at time (for phase alignment)
sessionState.requestBeatAtTime(beat, hostTime, quantum);

// Force beat position (overrides phase alignment)
sessionState.forceBeatAtTime(beat, hostTime, quantum);

// Start/stop
sessionState.setIsPlaying(true, hostTime);
bool playing = sessionState.isPlaying();

// Commit changes back
link.commitAudioSessionState(sessionState);
```

### Audio Thread vs App Thread

```cpp
// Audio thread (realtime-safe):
auto state = link.captureAudioSessionState();
// ... modify state ...
link.commitAudioSessionState(state);

// App thread (not realtime-safe):
auto state = link.captureAppSessionState();
// ... modify state ...
link.commitAppSessionState(state);
```

### Latency Compensation

Output latency must be added to system time values before passing to Link methods:

```cpp
// In audio callback:
auto hostTime = currentHostTime + outputLatency;
auto beat = sessionState.beatAtTime(hostTime, quantum);
```

This ensures devices synchronize at speaker output time, not callback invocation time.

## Platform Support

| Platform | Minimum Required | Optional |
|----------|------------------|----------|
| Windows | MSVC 17 2022 | Steinberg ASIO SDK 2.3 |
| macOS | Xcode 16.2.0 | -- |
| Linux | Clang 13 / GCC 10 | libportaudio19-dev |
| iOS | Use LinkKit SDK | -- |

## Language Bindings

### Node.js
- **@ktamas77/abletonlink**: https://www.npmjs.com/package/@ktamas77/abletonlink
- Node.js native addon wrapping the Link C++ SDK

### Python
- **link-python**: Python bindings for Ableton Link (available on PyPI)

### Other
- Link is integrated into many DAWs and music apps (Logic Pro, Reason, Serato DJ, etc.)
- Full list of Link-enabled apps: https://www.ableton.com/en/link/

## Links

- **Official site**: https://www.ableton.com/en/link/
- **Documentation**: https://ableton.github.io/link/
- **GitHub**: https://github.com/Ableton/link
- **LinkKit (iOS)**: https://github.com/Ableton/LinkKit
- **FAQ**: https://help.ableton.com/hc/en-us/articles/209776125
- **Live manual reference**: https://www.ableton.com/en/manual/synchronizing-with-link-tempo-follower-and-midi/
- **Test Plan**: TEST-PLAN.md in the repository
