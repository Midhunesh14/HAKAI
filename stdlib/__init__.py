"""HAKAI Standard Library Package."""

import os
import sys
from typing import List, Optional

try:
    import importlib.resources as importlib_resources
except ImportError:
    import importlib_resources  # type: ignore


def get_stdlib_path() -> Optional[str]:
    """Return the filesystem directory path containing standard library .hakai files."""
    # 1. Environment variable override
    env_path = os.environ.get("HAKAI_STDLIB_PATH")
    if env_path and os.path.isdir(env_path):
        return env_path

    # 2. Standalone frozen bundle (PyInstaller)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        frozen_path = os.path.join(getattr(sys, "_MEIPASS"), "stdlib")
        if os.path.isdir(frozen_path):
            return frozen_path

    # 3. Packaged resources via importlib.resources
    try:
        traversable = importlib_resources.files("stdlib")
        # In Python 3.10+, as_file or converting to str if on disk
        if hasattr(traversable, "is_dir") and traversable.is_dir():
            # Check if an actual directory on filesystem
            path_str = str(traversable)
            if os.path.isdir(path_str):
                return path_str
    except Exception:
        pass

    # 4. Fallback relative to this file
    this_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(this_dir):
        return this_dir

    return None
