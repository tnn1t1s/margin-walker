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
    return {"track_index": track_index, "count": result[0] if result else 0}


def get_device_names(track_index: int) -> dict:
    """Get names of all devices on a track.

    Args:
        track_index: Index of the track.

    Returns:
        Dict with list of device names and indices.
    """
    count_result = get_client().query("/live/track/get/num_devices", track_index)
    count = count_result[0] if count_result else 0
    devices = []
    for i in range(count):
        result = get_client().query("/live/device/get/name", track_index, i)
        devices.append({"index": i, "name": result[0] if result else f"Device {i}"})
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
    num_params = c.query("/live/device/get/num_parameters", track_index, device_index)
    count = num_params[0] if num_params else 0
    params = []
    for i in range(count):
        name = c.query("/live/device/get/parameter/name", track_index, device_index, i)
        value = c.query("/live/device/get/parameter/value", track_index, device_index, i)
        pmin = c.query("/live/device/get/parameter/min", track_index, device_index, i)
        pmax = c.query("/live/device/get/parameter/max", track_index, device_index, i)
        params.append({
            "index": i,
            "name": name[0] if name else f"Param {i}",
            "value": value[0] if value else None,
            "min": pmin[0] if pmin else None,
            "max": pmax[0] if pmax else None,
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
