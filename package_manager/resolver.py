"""Dependency resolver for HPM."""

from __future__ import annotations

import os
from typing import Dict, List, Set
from package_manager.package import PackageMetadata
from package_manager.repository import PackageRepository


class DependencyResolver:
    """Resolves transitive package dependencies and generates installation plans."""

    def __init__(self, repository: PackageRepository) -> None:
        self.repository = repository

    def resolve(self, root_manifest: PackageMetadata) -> List[PackageMetadata]:
        resolved: Dict[str, PackageMetadata] = {}
        visited: Set[str] = set()

        def _resolve_deps(deps: Dict[str, str], path_chain: List[str]) -> None:
            for dep_name, version in deps.items():
                if dep_name in path_chain:
                    raise ValueError(
                        f"Circular dependency detected: {' -> '.join(path_chain + [dep_name])}"
                    )
                if dep_name in resolved:
                    continue

                pkg_dir = self.repository.find_package(dep_name)
                if not pkg_dir:
                    # If not found in repo, could be local directory
                    if os.path.isdir(dep_name) and os.path.isfile(os.path.join(dep_name, "hakai.toml")):
                        pkg_dir = dep_name
                    else:
                        raise FileNotFoundError(f"Package '{dep_name}' could not be located.")

                meta = PackageMetadata.from_toml_file(os.path.join(pkg_dir, "hakai.toml"))
                resolved[dep_name] = meta
                _resolve_deps(meta.dependencies, path_chain + [dep_name])

        _resolve_deps(root_manifest.dependencies, [root_manifest.name])
        return list(resolved.values())
