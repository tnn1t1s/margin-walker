"""Scene operations — create, delete, launch, duplicate."""

from ..lib import get_client


def get_scene_count() -> dict:
    """Get the number of scenes in the Live set.

    Returns:
        Dict with scene count.
    """
    result = get_client().query("/live/song/get/num_scenes")
    return {"count": result[0] if result else 0}


def get_scene_names() -> dict:
    """Get names of all scenes.

    Returns:
        Dict with list of scene names and indices.
    """
    count_result = get_client().query("/live/song/get/num_scenes")
    count = count_result[0] if count_result else 0
    scenes = []
    for i in range(count):
        result = get_client().query("/live/scene/get/name", i)
        scenes.append({"index": i, "name": result[0] if result else f"Scene {i}"})
    return {"scenes": scenes}


def create_scene(index: int = -1) -> dict:
    """Create a new scene.

    Args:
        index: Position to insert scene (-1 for end).

    Returns:
        Dict with status.
    """
    get_client().send("/live/song/create_scene", index)
    return {"status": "created", "index": index}


def delete_scene(scene_index: int) -> dict:
    """Delete a scene by index.

    Args:
        scene_index: Index of the scene to delete.

    Returns:
        Dict with status.
    """
    get_client().send("/live/song/delete_scene", scene_index)
    return {"status": "deleted", "scene_index": scene_index}


def fire_scene(scene_index: int) -> dict:
    """Launch/fire a scene (triggers all clips in that row).

    Args:
        scene_index: Index of the scene to fire.

    Returns:
        Dict with status.
    """
    get_client().send("/live/scene/fire", scene_index)
    return {"status": "fired", "scene_index": scene_index}


def set_scene_name(scene_index: int, name: str) -> dict:
    """Rename a scene.

    Args:
        scene_index: Index of the scene.
        name: New name for the scene.

    Returns:
        Dict with status.
    """
    get_client().send("/live/scene/set/name", scene_index, name)
    return {"status": "renamed", "scene_index": scene_index, "name": name}


def duplicate_scene(scene_index: int) -> dict:
    """Duplicate a scene.

    Args:
        scene_index: Index of the scene to duplicate.

    Returns:
        Dict with status.
    """
    get_client().send("/live/song/duplicate_scene", scene_index)
    return {"status": "duplicated", "scene_index": scene_index}
