# Macros

Capture LLM tool sequences as replayable slash commands. The LLM figures out the tool calls once, you replay them instantly forever — no cloud inference, no latency.

## How It Works

```
Capture → Store → Replay
```

1. You send free text to the LLM agent — it resolves track names, figures out parameters, calls tools
2. `/save <name>` snapshots those tool calls into a JSON file
3. `/<name>` replays the exact same calls with no LLM involved

Macros are stored at the tool function level (`set_track_mute`, `set_track_volume`, etc.), not the slash command level. This means they call the Ableton OSC functions directly.

## Quick Start

```
> mute all tracks except the chords
[yellow]thinking...[/yellow]
  → set_track_mute({"track_index": 0, "muted": true})
  → set_track_mute({"track_index": 1, "muted": true})
  → set_track_mute({"track_index": 3, "muted": true})
[cyan]Done! Muted tracks 0, 1, 3[/cyan]

> /save chords-mute
[green]Saved macro 'chords-mute' (3 steps)[/green]

> /chords-mute
[green]set_track_mute → ok | set_track_mute → ok | set_track_mute → ok[/green]
```

## Commands

### `/save <name>`

Save the last LLM tool call sequence as a named macro.

```
> send the hats to the reverb bus at 40%
> /save hats-verb
[green]Saved macro 'hats-verb' (3 steps)[/green]
```

Rules:
- Name cannot conflict with a built-in command (`play`, `mute`, `vol`, etc.)
- Requires a prior LLM session with at least one tool call
- Overwrites if a macro with the same name already exists

### `/macros`

List all saved macros with step counts and the original prompt.

```
> /macros
chords-mute (3 steps) — "mute all tracks except the chords"
hats-verb (3 steps) — "send the hats to the reverb bus at 40%"
dark-mix (7 steps) — "mix this dark — roll off highs, heavy reverb"
```

### `/macro-show <name>`

Inspect the steps in a macro — useful for debugging or understanding what it does.

```
> /macro-show chords-mute
Macro: chords-mute
Prompt: "mute all tracks except the chords"
  1. set_track_mute({'track_index': 0, 'muted': True})
  2. set_track_mute({'track_index': 1, 'muted': True})
  3. set_track_mute({'track_index': 3, 'muted': True})
```

### `/macro-delete <name>`

Remove a saved macro.

```
> /macro-delete chords-mute
[green]Deleted macro 'chords-mute'[/green]
```

## Examples

### Performance prep — build a command palette

Use the LLM to set up macros before a live set:

```
> mute everything except drums and bass
> /save drums-bass

> solo just the 909
> /save 909-solo

> set all sends to reverb bus at 60%
> /save wet

> pull all sends to reverb bus to zero
> /save dry

> set tempo to 130 and fire scene 0
> /save drop
```

Then during performance — instant, no waiting:

```
> /drums-bass
> /wet
> /drop
> /909-solo
> /dry
```

### Mixing presets

```
> mix this like a dub record — heavy reverb, bass forward, everything else way back
> /save dub-mix

> flatten the mix — all volumes to 0.85, sends to zero
> /save flat-mix

> pan the three synth tracks hard left, center, hard right
> /save stereo-spread
```

### Track management

```
> arm all the MIDI tracks for recording
> /save arm-all

> mute all the noise tracks
> /save noise-off

> unmute everything
> /save unmute-all
```

## Storage

Macros persist in `~/.margin-walker/macros.json`. The format:

```json
{
  "chords-mute": {
    "steps": [
      {"function_name": "set_track_mute", "args": {"track_index": 0, "muted": true}},
      {"function_name": "set_track_mute", "args": {"track_index": 1, "muted": true}},
      {"function_name": "set_track_mute", "args": {"track_index": 3, "muted": true}}
    ],
    "created_from": "mute all tracks except the chords"
  }
}
```

You can edit this file directly if needed — the TUI reloads it on startup.

## Limitations

Macros are **static replay** — they store exact track indices and parameter values at save time.

- If you reorder tracks, saved indices will be wrong
- If you rename tracks, the macro still uses the old indices
- No parameterization — `/chords-mute bass` won't re-resolve "bass" at runtime

These are planned for v2 (track name re-resolution, parameterized macros, auto-generated inverses).
