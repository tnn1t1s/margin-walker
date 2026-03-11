"""Mixer operations — master volume, crossfader, send levels, return tracks."""

from ..lib import get_client


def get_master_volume() -> dict:
    """Get the master track volume level.

    Returns:
        Dict with master volume (0.0-1.0).
    """
    result = get_client().query("/live/master/get/volume")
    return {"master_volume": result[0] if result else None}


def set_master_volume(volume: float) -> dict:
    """Set the master track volume.

    Args:
        volume: Volume level (0.0 to 1.0).

    Returns:
        Dict with new volume.
    """
    volume = max(0.0, min(1.0, volume))
    get_client().send("/live/master/set/volume", volume)
    return {"master_volume": volume}


def get_master_pan() -> dict:
    """Get the master track panning.

    Returns:
        Dict with master panning (-1.0 to 1.0).
    """
    result = get_client().query("/live/master/get/panning")
    return {"master_pan": result[0] if result else None}


def get_master_devices() -> dict:
    """Get names of devices on the master track.

    Returns:
        Dict with list of device names.
    """
    result = get_client().query("/live/master/get/devices/name")
    return {"devices": list(result) if result else []}


def get_crossfader() -> dict:
    """Get the crossfader position.

    Returns:
        Dict with crossfader position (-1.0 A to 1.0 B).
    """
    result = get_client().query("/live/master/get/crossfader")
    return {"crossfader": result[0] if result else None}


def set_crossfader(position: float) -> dict:
    """Set the crossfader position.

    Args:
        position: Crossfader position (-1.0 A to 1.0 B, 0.0 center).

    Returns:
        Dict with position.
    """
    position = max(-1.0, min(1.0, position))
    get_client().send("/live/master/set/crossfader", position)
    return {"crossfader": position}


def get_return_track_count() -> dict:
    """Get the number of return tracks.

    Returns:
        Dict with return track count.
    """
    result = get_client().query("/live/song/get/num_return_tracks")
    return {"count": result[0] if result else 0}


def get_return_track_names() -> dict:
    """Get names of all return tracks.

    Returns:
        Dict with list of return track names.
    """
    result = get_client().query("/live/song/get/return_track_names")
    tracks = [{"index": i, "name": name} for i, name in enumerate(result)]
    return {"return_tracks": tracks}


def get_return_track_devices(return_index: int) -> dict:
    """Get devices on a return track.

    Args:
        return_index: Index of the return track.

    Returns:
        Dict with list of device names.
    """
    result = get_client().query("/live/return/get/devices/name", return_index)
    return {"return_index": return_index, "devices": list(result[1:]) if len(result) > 1 else []}


def set_return_volume(return_index: int, volume: float) -> dict:
    """Set a return track's volume.

    Args:
        return_index: Index of the return track.
        volume: Volume level (0.0 to 1.0).

    Returns:
        Dict with status.
    """
    volume = max(0.0, min(1.0, volume))
    get_client().send("/live/return/set/volume", return_index, volume)
    return {"return_index": return_index, "volume": volume}


def set_send_level(track_index: int, send_index: int, level: float) -> dict:
    """Set a track's send level to a return track.

    Args:
        track_index: Index of the source track.
        send_index: Index of the send (corresponds to return track).
        level: Send level (0.0 to 1.0).

    Returns:
        Dict with status.
    """
    level = max(0.0, min(1.0, level))
    get_client().send("/live/track/set/send", track_index, send_index, level)
    return {"track_index": track_index, "send_index": send_index, "level": level}


def get_send_level(track_index: int, send_index: int) -> dict:
    """Get a track's send level.

    Args:
        track_index: Index of the source track.
        send_index: Index of the send.

    Returns:
        Dict with send level.
    """
    result = get_client().query("/live/track/get/send", track_index, send_index)
    return {"track_index": track_index, "send_index": send_index, "level": result[2] if len(result) > 2 else None}
