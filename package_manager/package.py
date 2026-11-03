"""Package metadata and manifest (hakai.toml) management for HPM."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python 3.10


@dataclass
class PackageMetadata:
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    entry: str = "main.hakai"
    dependencies: Dict[str, str] = field(default_factory=dict)

    def to_toml(self) -> str:
        lines = [
            "[package]",
            f'name = "{self.name}"',
            f'version = "{self.version}"',
            f'description = "{self.description}"',
            f'author = "{self.author}"',
            f'license = "{self.license}"',
            f'entry = "{self.entry}"',
            "",
            "[dependencies]",
        ]
        for dep, ver in self.dependencies.items():
            lines.append(f'{dep} = "{ver}"')
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def from_toml_file(cls, path: str) -> PackageMetadata:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Manifest not found: {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        pkg_info = data.get("package", {})
        deps = data.get("dependencies", {})

        return cls(
            name=pkg_info.get("name", "unnamed"),
            version=pkg_info.get("version", "1.0.0"),
            description=pkg_info.get("description", ""),
            author=pkg_info.get("author", ""),
            license=pkg_info.get("license", "MIT"),
            entry=pkg_info.get("entry", "main.hakai"),
            dependencies=deps,
        )

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_toml())

