"""Transport controls — play, stop, record, tempo, time signature."""

from ..lib import get_client


def play() -> dict:
    """Start playback in Ableton Live.

    Returns:
        Dict with status confirmation.
    """
    get_client().send("/live/song/start_playing")
    return {"status": "playing"}


def stop() -> dict:
    """Stop playback in Ableton Live.

    Returns:
        Dict with status confirmation.
    """
    get_client().send("/live/song/stop_playing")
    return {"status": "stopped"}


def toggle_record() -> dict:
    """Toggle session record in Ableton Live.

    Returns:
        Dict with status confirmation.
    """
    get_client().send("/live/song/set/record_mode", 1)
    return {"status": "record_toggled"}


def get_tempo() -> dict:
    """Get the current tempo (BPM) of the Ableton Live set.

    Returns:
        Dict with current tempo value.
    """
    result = get_client().query("/live/song/get/tempo")
    return {"tempo": result[0] if result else None}


def set_tempo(bpm: float) -> dict:
    """Set the tempo (BPM) of the Ableton Live set.

    Args:
        bpm: Tempo in beats per minute (20.0-999.0).

    Returns:
        Dict with the new tempo value.
    """
    bpm = max(20.0, min(999.0, bpm))
    get_client().send("/live/song/set/tempo", bpm)
    return {"tempo": bpm}


def get_time_signature() -> dict:
    """Get the current time signature.

    Returns:
        Dict with numerator and denominator.
    """
    result = get_client().query("/live/song/get/signature_numerator")
    result2 = get_client().query("/live/song/get/signature_denominator")
    return {
        "numerator": result[0] if result else None,
        "denominator": result2[0] if result2 else None,
    }


def set_time_signature(numerator: int = 4, denominator: int = 4) -> dict:
    """Set the time signature.

    Args:
        numerator: Beats per bar (1-99).
        denominator: Beat unit (1, 2, 4, 8, 16).

    Returns:
        Dict with new time signature.
    """
    get_client().send("/live/song/set/signature_numerator", numerator)
    get_client().send("/live/song/set/signature_denominator", denominator)
    return {"numerator": numerator, "denominator": denominator}


def get_is_playing() -> dict:
    """Check if Ableton Live is currently playing.

    Returns:
        Dict with is_playing boolean.
    """
    result = get_client().query("/live/song/get/is_playing")
    return {"is_playing": bool(result[0]) if result else False}


def undo() -> dict:
    """Undo the last action in Ableton Live.

    Returns:
        Dict with status confirmation.
    """
    get_client().send("/live/song/undo")
    return {"status": "undone"}


def redo() -> dict:
    """Redo the last undone action in Ableton Live.

    Returns:
        Dict with status confirmation.
    """
    get_client().send("/live/song/redo")
    return {"status": "redone"}
