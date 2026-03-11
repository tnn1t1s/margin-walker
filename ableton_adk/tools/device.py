"""Device operations — load instruments/effects, get/set parameters."""

from ..lib import get_client


def get_device_count(track_index: int) -> dict:
    """Get the number of devices on a track.

    Args:
        track_index: Index of the track.

    Returns:
        Dict with device count.
    """
    result = get_client().query("/live/track/get/num_devices", track_index)
    return {"track_index": track_index, "count": result[1] if len(result) > 1 else 0}


def get_device_names(track_index: int) -> dict:
    """Get names of all devices on a track.

    Args:
        track_index: Index of the track.

    Returns:
        Dict with list of device names and indices.
    """
    result = get_client().query("/live/track/get/devices/name", track_index)
    devices = [{"index": i, "name": name} for i, name in enumerate(result[1:])]
    return {"track_index": track_index, "devices": devices}


def get_device_parameters(track_index: int, device_index: int) -> dict:
    """Get all parameters for a device.

    Args:
        track_index: Index of the track.
        device_index: Index of the device on the track.

    Returns:
        Dict with list of parameter names, values, min, max.
    """
    c = get_client()
    names = c.query("/live/device/get/parameters/name", track_index, device_index)
    values = c.query("/live/device/get/parameters/value", track_index, device_index)
    mins = c.query("/live/device/get/parameters/min", track_index, device_index)
    maxs = c.query("/live/device/get/parameters/max", track_index, device_index)
    n_skip = 2
    params = []
    for i in range(len(names) - n_skip):
        params.append({
            "index": i,
            "name": names[n_skip + i] if n_skip + i < len(names) else f"Param {i}",
            "value": values[n_skip + i] if n_skip + i < len(values) else None,
            "min": mins[n_skip + i] if n_skip + i < len(mins) else None,
            "max": maxs[n_skip + i] if n_skip + i < len(maxs) else None,
        })
    return {"track_index": track_index, "device_index": device_index, "parameters": params}


def set_device_parameter(
    track_index: int, device_index: int, parameter_index: int, value: float
) -> dict:
    """Set a device parameter value.

    Args:
        track_index: Index of the track.
        device_index: Index of the device.
        parameter_index: Index of the parameter.
        value: New value for the parameter.

    Returns:
        Dict with status.
    """
    get_client().send(
        "/live/device/set/parameter/value",
        track_index, device_index, parameter_index, value,
    )
    return {
        "status": "set",
        "track_index": track_index,
        "device_index": device_index,
        "parameter_index": parameter_index,
        "value": value,
    }


def set_device_enabled(track_index: int, device_index: int, enabled: bool = True) -> dict:
    """Enable or disable (bypass) a device.

    Args:
        track_index: Index of the track.
        device_index: Index of the device.
        enabled: True to enable, False to bypass.

    Returns:
        Dict with status.
    """
    get_client().send(
        "/live/device/set/is_active",
        track_index, device_index, int(enabled),
    )
    return {"track_index": track_index, "device_index": device_index, "enabled": enabled}
