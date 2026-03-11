# AI Agents & Ableton Live Integration

## Overview

The intersection of AI agents and Ableton Live is a rapidly evolving space. The primary integration mechanism is the **Model Context Protocol (MCP)**, introduced by Anthropic in November 2024, which standardizes how LLMs connect to external tools. Multiple MCP servers now exist for Ableton Live, along with Google's Magenta Studio for ML-powered music generation.

---

## MCP Servers for Ableton Live

### 1. AbletonMCP (ahujasid/ableton-mcp) -- Most Popular

The leading MCP server for Ableton Live control via AI assistants.

- **Repository**: https://github.com/ahujasid/ableton-mcp
- **Stats**: ~1,900 stars, 218 forks
- **Compatibility**: Claude Desktop, Cursor; Live 10+

#### Architecture

```
┌──────────────┐     MCP      ┌──────────────┐    TCP/Socket   ┌───────────────┐
│  Claude      │ ───────────> │  MCP Server  │ ─────────────> │  Ableton Live │
│  Desktop /   │              │  (server.py) │                │  (Remote      │
│  Cursor      │ <─────────── │              │ <───────────── │   Script)     │
└──────────────┘              └──────────────┘                └───────────────┘
```

Two components:
1. **Ableton Remote Script** (`__init__.py`): Socket server running inside Live
2. **MCP Server** (`server.py`): Bridges Claude's MCP tool calls to the Remote Script

#### Installation

```bash
# Install via uvx (recommended)
# Add to claude_desktop_config.json:
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "uvx",
      "args": ["ableton-mcp"]
    }
  }
}
```

Then install the Remote Script:
1. Download `AbletonMCP_Remote_Script/__init__.py`
2. Place in Ableton's Remote Scripts folder
3. Select "AbletonMCP" in Settings > Link, Tempo & MIDI

#### Capabilities

- Create/edit MIDI and audio tracks
- Generate MIDI clips with notes
- Load instruments and effects from Ableton's browser
- Control transport (play, stop, tempo)
- Query session state
- Fire clips and scenes

#### Example Prompt

> "Create an 80s synthwave track with a bass line, pad chords, and arpeggio lead"

Claude orchestrates track creation, instrument loading, and clip generation through the MCP tools.

---

### 2. Ableton Live MCP Server (OSC-based, Simon-Kansara)

MCP server that bridges to Ableton via AbletonOSC.

- **Repository**: https://github.com/Simon-Kansara/ableton-live-mcp-server
- **Protocol**: OSC via AbletonOSC

#### Architecture

```
┌──────────────┐     MCP      ┌──────────────┐     OSC        ┌───────────────┐
│  AI Client   │ ───────────> │  MCP Server  │ ─────────────> │  AbletonOSC   │
│  (Claude)    │              │  (FastMCP)   │   port 11000   │  (Remote      │
│              │ <─────────── │              │ <───────────── │   Script)     │
└──────────────┘              │  port 65432  │   port 11001   └───────────────┘
                              └──────────────┘
```

#### Setup

```bash
# Requirements: Python 3.8+, python-osc, fastmcp, uv
uv sync  # Install dependencies

# Claude Desktop config:
{
  "mcpServers": {
    "Ableton Live Controller": {
      "command": "/path/to/python",
      "args": ["/path/to/mcp_ableton_server.py"]
    }
  }
}
```

Requires AbletonOSC installed in Ableton Live.

#### Use Cases

- "Set input routing for all vocal tracks to Ext. In 2"
- "Prepare a recording session for a rock band"
- Track/device management, audio routing, parameter automation

---

### 3. ableton-copilot-mcp (Built on ableton-js)

MCP server built on top of the ableton-js Node.js library.

- **Repository**: https://github.com/xiaolaa2/ableton-copilot-mcp
- **npm**: https://www.npmjs.com/package/ableton-copilot-mcp

Includes Arrangement View operations: song management, track control, MIDI editing, audio recording.

---

### 4. Ableton MCP Extended

- **Stats**: 53 stars, newer project
- **Compatibility**: Claude Desktop, Gemini CLI, Cursor, ElevenLabs MCP; Live 11+
- **Unique features**: Voice/audio generation via ElevenLabs, UDP protocol, low-latency commands
- **Requirements**: Python 3.10+
- **Known limitations**: Automation points unstable, limited VST support, no arrangement view

---

### MCP Server Comparison

| Feature | ahujasid (Popular) | Simon-Kansara (OSC) | copilot-mcp | Extended |
|---------|-------------------|---------------------|-------------|----------|
| Protocol | TCP Socket | OSC (AbletonOSC) | UDP (ableton-js) | UDP |
| Stars | ~1,900 | ~50 | ~30 | ~53 |
| AI Clients | Claude, Cursor | Claude | Claude | Claude, Gemini, Cursor |
| Live Version | 10+ | 11+ | 11+ | 11+ |
| Voice Control | No | No | No | Yes (ElevenLabs) |
| Install Method | uvx | uv sync | npm | pip |

---

## Google Magenta Studio

### What It Is

Magenta Studio is a collection of free Max for Live devices from Google's Magenta research lab that uses machine learning to assist with music creation. It runs ML models **locally** (no internet required).

- **Website**: https://magenta.withgoogle.com/studio/
- **Version**: 2.0
- **Requirements**: Ableton Live 10.1 Suite or later (or Max 8)
- **Installation**: Drag `.amxd` file into any MIDI track

### Five ML Tools

| Tool | Input | Output | ML Model | Description |
|------|-------|--------|----------|-------------|
| **Generate** | None | 4-bar phrase | VAE | Creates melodies/rhythms from nothing. Trained on millions of melodies. |
| **Continue** | Melody/drum clip | Extended clip (up to 32 measures) | RNN | Extends existing patterns by detecting duration, key, timing. |
| **Interpolate** | Two clips | Up to 16 intermediate clips | VAE | Morphs between two patterns in compressed latent space. |
| **Groove** | Drum clip | Humanized drum clip | Trained on 15hrs of drummer MIDI | Adjusts timing and velocity for human feel. |
| **Drumify** | Any rhythm clip | Drum groove | Same as Groove | Converts melody/bass rhythm into drum patterns. |

All tools have a **temperature** slider controlling randomness (low = conservative, high = experimental).

### Limitations

- Melody inputs must be **monophonic** (single notes only)
- Drum inputs use a specific 9-instrument MIDI mapping
- Models are pre-trained (no custom training)
- Max for Live required (Live Suite or Max 8 add-on)

### Research Paper

- "Magenta Studio: Augmenting Creativity with Deep Learning in Ableton Live" -- https://research.google/pubs/magenta-studio-augmenting-creativity-with-deep-learning-in-ableton-live/

---

## Google ADK (Agent Development Kit)

### Current State

As of March 2026, there is **no official Google ADK integration specifically for Ableton Live**. However, the ADK architecture could support it:

- **ADK**: Open-source framework for building agentic workflows -- https://google.github.io/adk-docs/
- **ADK Integrations**: Supports third-party tools and integrations -- https://google.github.io/adk-docs/integrations/
- **Potential**: ADK agents could use MCP servers (like the ones above) as tools, since ADK supports MCP tool integration

### Building an ADK + Ableton Agent

A Google ADK agent could be created to control Ableton by:

1. Using an existing MCP server as a tool (ADK supports MCP)
2. Directly communicating via OSC (using python-osc)
3. Using the ableton-liveapi-tools TCP interface
4. Combining with Magenta for AI-generated MIDI content

---

## Other AI + Ableton Projects

### MIDI Agent
- **URL**: https://www.midiagent.com/ai-midi-generator-for-ableton-live
- AI MIDI generator that creates melodies, chord progressions, and compositions from natural language prompts
- Drag-and-drop MIDI output into Ableton

### Ableton Live AI Assistant
- **URL**: https://ableton-ai-agent.vercel.app/
- Web-based AI assistant providing expert help for Ableton Live workflows

### Ableton's Own AI Research
- Ableton has published articles on AI and music-making: https://www.ableton.com/en/blog/ai-and-music-making-the-state-of-play/
- No official AI integration in Live as of 2026, but actively researching

---

## Recommended Stack for AI-Powered Ableton Control

For building an AI agent that controls Ableton Live:

```
┌──────────────────────────────────────────────────────┐
│  AI Agent Layer                                       │
│  (Google ADK / LangChain / Custom)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │ LLM         │  │ Magenta     │  │ Custom ML    │ │
│  │ (Gemini/    │  │ (Generate,  │  │ (Trained on  │ │
│  │  Claude)    │  │  Continue)  │  │  your music) │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘ │
└─────────┼────────────────┼────────────────┼──────────┘
          │                │                │
          ▼                ▼                ▼
┌──────────────────────────────────────────────────────┐
│  Control Layer                                        │
│  ┌───────────┐  ┌────────────┐  ┌──────────────────┐ │
│  │ MCP Server│  │ AbletonOSC │  │ MIDI (rtmidi)    │ │
│  │ (session  │  │ (params,   │  │ (note input,     │ │
│  │  control) │  │  transport)│  │  real-time perf) │ │
│  └─────┬─────┘  └─────┬──────┘  └────────┬─────────┘ │
└────────┼──────────────┼──────────────────┼───────────┘
         │              │                  │
         ▼              ▼                  ▼
┌──────────────────────────────────────────────────────┐
│  Ableton Live                                         │
│  (Remote Scripts, AbletonOSC, Virtual MIDI, M4L)     │
└──────────────────────────────────────────────────────┘
```

### Recommended Approach

1. **Primary control**: AbletonOSC or ableton-liveapi-tools (broadest API coverage)
2. **AI agent framework**: Google ADK or direct LLM integration via MCP
3. **Music generation**: Magenta Studio for in-DAW ML, or external ML models generating MIDI
4. **Real-time input**: MIDI via rtmidi/mido for note-level control
5. **Sync**: Ableton Link for multi-device tempo synchronization

## Links

- **AbletonMCP**: https://github.com/ahujasid/ableton-mcp
- **Ableton Live MCP Server**: https://github.com/Simon-Kansara/ableton-live-mcp-server
- **ableton-copilot-mcp**: https://github.com/xiaolaa2/ableton-copilot-mcp
- **Magenta Studio**: https://magenta.withgoogle.com/studio/
- **Google ADK**: https://google.github.io/adk-docs/
- **MCP Options Comparison**: https://www.mslinn.com/av_studio/555-ableton-mcp-options.html
- **Ableton on AI**: https://www.ableton.com/en/blog/ai-and-music-making-the-state-of-play/
