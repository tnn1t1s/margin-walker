"""Clip operations — create, add MIDI notes, launch, stop, duplicate."""

from ..lib import get_client


def create_clip(track_index: int, scene_index: int, length: float = 4.0) -> dict:
    """Create a new empty MIDI clip in a slot.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene (clip slot).
        length: Length in beats (default 4.0 = 1 bar at 4/4).

    Returns:
        Dict with status and clip location.
    """
    get_client().send("/live/clip_slot/create_clip", track_index, scene_index, length)
    return {
        "status": "created",
        "track_index": track_index,
        "scene_index": scene_index,
        "length": length,
    }


def delete_clip(track_index: int, scene_index: int) -> dict:
    """Delete a clip from a slot.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.

    Returns:
        Dict with status.
    """
    get_client().send("/live/clip_slot/delete_clip", track_index, scene_index)
    return {"status": "deleted", "track_index": track_index, "scene_index": scene_index}


def add_notes(
    track_index: int,
    scene_index: int,
    notes: list[dict],
) -> dict:
    """Add MIDI notes to a clip.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.
        notes: List of note dicts, each with keys:
            pitch (int 0-127), start (float beats), duration (float beats),
            velocity (int 0-127), mute (bool, optional).

    Returns:
        Dict with status and count of notes added.
    """
    c = get_client()
    for note in notes:
        pitch = note["pitch"]
        start = note["start"]
        duration = note["duration"]
        velocity = note.get("velocity", 100)
        mute = int(note.get("mute", False))
        c.send(
            "/live/clip/add/notes",
            track_index, scene_index,
            pitch, start, duration, velocity, mute,
        )
    return {
        "status": "notes_added",
        "track_index": track_index,
        "scene_index": scene_index,
        "count": len(notes),
    }


def get_notes(track_index: int, scene_index: int) -> dict:
    """Get all MIDI notes from a clip.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.

    Returns:
        Dict with list of notes (pitch, start, duration, velocity, mute).
    """
    result = get_client().query("/live/clip/get/notes", track_index, scene_index)
    notes = []
    if result:
        i = 0
        while i + 4 < len(result):
            notes.append({
                "pitch": result[i],
                "start": result[i + 1],
                "duration": result[i + 2],
                "velocity": result[i + 3],
                "mute": bool(result[i + 4]) if i + 4 < len(result) else False,
            })
            i += 5
    return {"track_index": track_index, "scene_index": scene_index, "notes": notes}


def remove_notes(
    track_index: int,
    scene_index: int,
    from_time: float = 0.0,
    time_span: float = 128.0,
    from_pitch: int = 0,
    pitch_span: int = 127,
) -> dict:
    """Remove MIDI notes from a clip within a range.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.
        from_time: Start time in beats.
        time_span: Duration span in beats.
        from_pitch: Lowest pitch to remove.
        pitch_span: Pitch range to remove.

    Returns:
        Dict with status.
    """
    get_client().send(
        "/live/clip/remove/notes",
        track_index, scene_index,
        from_time, time_span, from_pitch, pitch_span,
    )
    return {"status": "notes_removed"}


def fire_clip(track_index: int, scene_index: int) -> dict:
    """Launch/fire a clip.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.

    Returns:
        Dict with status.
    """
    get_client().send("/live/clip/fire", track_index, scene_index)
    return {"status": "fired", "track_index": track_index, "scene_index": scene_index}


def stop_clip(track_index: int, scene_index: int) -> dict:
    """Stop a playing clip.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.

    Returns:
        Dict with status.
    """
    get_client().send("/live/clip/stop", track_index, scene_index)
    return {"status": "stopped", "track_index": track_index, "scene_index": scene_index}


def duplicate_clip(track_index: int, scene_index: int) -> dict:
    """Duplicate a clip to the next available slot.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene to duplicate.

    Returns:
        Dict with status.
    """
    get_client().send("/live/clip_slot/duplicate_clip_to", track_index, scene_index, track_index, scene_index + 1)
    return {"status": "duplicated", "source_scene": scene_index, "target_scene": scene_index + 1}


def set_clip_name(track_index: int, scene_index: int, name: str) -> dict:
    """Set the name of a clip.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.
        name: New clip name.

    Returns:
        Dict with status.
    """
    get_client().send("/live/clip/set/name", track_index, scene_index, name)
    return {"status": "renamed", "name": name}


def set_clip_loop(
    track_index: int,
    scene_index: int,
    loop_start: float = 0.0,
    loop_end: float = 4.0,
) -> dict:
    """Set clip loop points.

    Args:
        track_index: Index of the track.
        scene_index: Index of the scene.
        loop_start: Loop start in beats.
        loop_end: Loop end in beats.

    Returns:
        Dict with status.
    """
    c = get_client()
    c.send("/live/clip/set/loop_start", track_index, scene_index, loop_start)
    c.send("/live/clip/set/loop_end", track_index, scene_index, loop_end)
    return {"status": "loop_set", "loop_start": loop_start, "loop_end": loop_end}
