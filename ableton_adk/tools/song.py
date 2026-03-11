"""Song-level operations — get set info, quantization, groove."""

from ..lib import get_client


def get_song_info() -> dict:
    """Get overview of the current Ableton Live set.

    Returns:
        Dict with tempo, time signature, track count, scene count, playing state.
    """
    c = get_client()
    tempo = c.query("/live/song/get/tempo")
    sig_num = c.query("/live/song/get/signature_numerator")
    sig_den = c.query("/live/song/get/signature_denominator")
    tracks = c.query("/live/song/get/num_tracks")
    scenes = c.query("/live/song/get/num_scenes")
    playing = c.query("/live/song/get/is_playing")
    return {
        "tempo": tempo[0] if tempo else None,
        "time_signature": f"{sig_num[0] if sig_num else '?'}/{sig_den[0] if sig_den else '?'}",
        "track_count": tracks[0] if tracks else 0,
        "scene_count": scenes[0] if scenes else 0,
        "is_playing": bool(playing[0]) if playing else False,
    }


def set_quantization(value: int) -> dict:
    """Set the global clip launch quantization.

    Args:
        value: Quantization value (0=None, 1=8 bars, 2=4 bars, 3=2 bars,
               4=1 bar, 5=1/2, 6=1/4, 7=1/8, 8=1/16, 9=1/32).

    Returns:
        Dict with status.
    """
    get_client().send("/live/song/set/clip_trigger_quantization", value)
    return {"quantization": value}


def set_groove_amount(amount: float) -> dict:
    """Set the global groove amount.

    Args:
        amount: Groove amount (0.0 to 1.0).

    Returns:
        Dict with status.
    """
    amount = max(0.0, min(1.0, amount))
    get_client().send("/live/song/set/groove_amount", amount)
    return {"groove_amount": amount}


def jump_to_time(time_beats: float) -> dict:
    """Jump to a specific time position in the song.

    Args:
        time_beats: Position in beats to jump to.

    Returns:
        Dict with status.
    """
    get_client().send("/live/song/set/current_song_time", time_beats)
    return {"position": time_beats}


def get_current_time() -> dict:
    """Get the current playback position.

    Returns:
        Dict with current time in beats.
    """
    result = get_client().query("/live/song/get/current_song_time")
    return {"time_beats": result[0] if result else 0.0}
