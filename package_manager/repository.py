"""Package repository lookup and registry integration for HPM."""

from __future__ import annotations

import os
from typing import Dict, List, Optional
from package_manager.package import PackageMetadata


class PackageRepository:
    """Manages package sources from local folders and user cache."""

    def __init__(self, search_paths: Optional[List[str]] = None) -> None:
        self.search_paths = search_paths or [
            os.path.expanduser("~/.hakai/cache"),
            os.path.join(os.getcwd(), "packages"),
        ]

    def find_package(self, package_name: str) -> Optional[str]:
        """Search registered paths for a directory containing hakai.toml."""
        for base in self.search_paths:
            candidate = os.path.join(base, package_name)
            manifest = os.path.join(candidate, "hakai.toml")
            if os.path.isfile(manifest):
                return candidate
        return None

    def list_available(self) -> Dict[str, str]:
        """List packages discovered in search paths."""
        results = {}
        for base in self.search_paths:
            if os.path.isdir(base):
                for entry in os.listdir(base):
                    full = os.path.join(base, entry)
                    if os.path.isdir(full) and os.path.isfile(os.path.join(full, "hakai.toml")):
                        try:
                            meta = PackageMetadata.from_toml_file(os.path.join(full, "hakai.toml"))
                            results[meta.name] = meta.version
                        except Exception:
                            pass
        return results
