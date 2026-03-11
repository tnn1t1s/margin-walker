"""Track operations — create, delete, rename, arm, solo, mute, volume, pan."""

from ..lib import get_client


def get_track_count() -> dict:
    """Get the number of tracks in the Live set.

    Returns:
        Dict with count of tracks.
    """
    result = get_client().query("/live/song/get/num_tracks")
    return {"count": result[0] if result else 0}


def get_track_names() -> dict:
    """Get names of all tracks in the Live set.

    Returns:
        Dict with list of track names and their indices.
    """
    count_result = get_client().query("/live/song/get/num_tracks")
    count = count_result[0] if count_result else 0
    tracks = []
    for i in range(count):
        result = get_client().query("/live/track/get/name", i)
        tracks.append({"index": i, "name": result[0] if result else f"Track {i}"})
    return {"tracks": tracks}


def create_midi_track(index: int = -1) -> dict:
    """Create a new MIDI track.

    Args:
        index: Position to insert track (-1 for end).

    Returns:
        Dict with status and track index.
    """
    get_client().send("/live/song/create_midi_track", index)
    return {"status": "created", "index": index}


def create_audio_track(index: int = -1) -> dict:
    """Create a new audio track.

    Args:
        index: Position to insert track (-1 for end).

    Returns:
        Dict with status and track index.
    """
    get_client().send("/live/song/create_audio_track", index)
    return {"status": "created", "index": index}


def delete_track(track_index: int) -> dict:
    """Delete a track by index.

    Args:
        track_index: Index of the track to delete.

    Returns:
        Dict with status confirmation.
    """
    get_client().send("/live/song/delete_track", track_index)
    return {"status": "deleted", "track_index": track_index}


def set_track_name(track_index: int, name: str) -> dict:
    """Rename a track.

    Args:
        track_index: Index of the track.
        name: New name for the track.

    Returns:
        Dict with status and new name.
    """
    get_client().send("/live/track/set/name", track_index, name)
    return {"status": "renamed", "track_index": track_index, "name": name}


def set_track_arm(track_index: int, armed: bool = True) -> dict:
    """Arm or disarm a track for recording.

    Args:
        track_index: Index of the track.
        armed: True to arm, False to disarm.

    Returns:
        Dict with status.
    """
    get_client().send("/live/track/set/arm", track_index, int(armed))
    return {"track_index": track_index, "armed": armed}


def set_track_mute(track_index: int, muted: bool = True) -> dict:
    """Mute or unmute a track.

    Args:
        track_index: Index of the track.
        muted: True to mute, False to unmute.

    Returns:
        Dict with status.
    """
    get_client().send("/live/track/set/mute", track_index, int(muted))
    return {"track_index": track_index, "muted": muted}


def set_track_solo(track_index: int, solo: bool = True) -> dict:
    """Solo or unsolo a track.

    Args:
        track_index: Index of the track.
        solo: True to solo, False to unsolo.

    Returns:
        Dict with status.
    """
    get_client().send("/live/track/set/solo", track_index, int(solo))
    return {"track_index": track_index, "solo": solo}


def set_track_volume(track_index: int, volume: float) -> dict:
    """Set track volume.

    Args:
        track_index: Index of the track.
        volume: Volume level (0.0 to 1.0).

    Returns:
        Dict with status.
    """
    volume = max(0.0, min(1.0, volume))
    get_client().send("/live/track/set/volume", track_index, volume)
    return {"track_index": track_index, "volume": volume}


def set_track_pan(track_index: int, pan: float) -> dict:
    """Set track panning.

    Args:
        track_index: Index of the track.
        pan: Pan position (-1.0 left to 1.0 right, 0.0 center).

    Returns:
        Dict with status.
    """
    pan = max(-1.0, min(1.0, pan))
    get_client().send("/live/track/set/panning", track_index, pan)
    return {"track_index": track_index, "pan": pan}


def get_track_info(track_index: int) -> dict:
    """Get detailed info about a track.

    Args:
        track_index: Index of the track.

    Returns:
        Dict with track name, arm, mute, solo, volume, pan state.
    """
    c = get_client()
    name = c.query("/live/track/get/name", track_index)
    arm = c.query("/live/track/get/arm", track_index)
    mute = c.query("/live/track/get/mute", track_index)
    solo = c.query("/live/track/get/solo", track_index)
    vol = c.query("/live/track/get/volume", track_index)
    pan = c.query("/live/track/get/panning", track_index)
    return {
        "track_index": track_index,
        "name": name[0] if name else None,
        "armed": bool(arm[0]) if arm else False,
        "muted": bool(mute[0]) if mute else False,
        "solo": bool(solo[0]) if solo else False,
        "volume": vol[0] if vol else None,
        "pan": pan[0] if pan else None,
    }
