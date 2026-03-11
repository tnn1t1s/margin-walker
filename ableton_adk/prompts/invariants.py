import sys
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "ableton-config"


def _load_config_text(filename: str) -> str:
    path = CONFIG_DIR / filename
    if not path.exists():
        print(
            f"FATAL: {path} not found. Copy ableton-config.example/ to ableton-config/ and customize.",
            file=sys.stderr,
        )
        sys.exit(1)
    return path.read_text()


INVARIANTS = _load_config_text("invariants.txt")
