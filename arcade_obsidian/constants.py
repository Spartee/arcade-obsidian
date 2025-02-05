import os
from typing import Any


def safe_float(value: Any, default: float) -> float:
    """
    Attempts to convert `value` to a float. If the conversion fails,
    returns the provided `default` value.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "/path/to/default/vault")
INDEX_POLL_INTERVAL = safe_float(os.getenv("INDEX_POLL_INTERVAL"), 60)
INDEX_START_DELAY = safe_float(os.getenv("INDEX_START_DELAY"), 5)
INDEX_STORAGE_PATH = os.path.abspath(
    os.path.expanduser(os.getenv("INDEX_STORAGE_PATH", "~/.arcade/obsidian"))
)
INDEX_NAME = os.getenv("INDEX_NAME", "index")
