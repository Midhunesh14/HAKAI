"""Package installer and lockfile manager for HPM."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from typing import Dict, List, Optional
from package_manager.package import PackageMetadata
from package_manager.repository import PackageRepository
from package_manager.resolver import DependencyResolver


class PackageInstaller:
    """Installs resolved packages into the local project environment (.hakai_packages)."""

    def __init__(self, project_dir: str = ".") -> None:
        self.project_dir = os.path.abspath(project_dir)
        self.packages_dir = os.path.join(self.project_dir, ".hakai_packages")
        self.lockfile_path = os.path.join(self.project_dir, "hakai.lock")
        self.manifest_path = os.path.join(self.project_dir, "hakai.toml")
        self.repo = PackageRepository(search_paths=[
            self.packages_dir,
            os.path.expanduser("~/.hakai/cache"),
            os.path.join(self.project_dir, "packages"),
        ])
        self.resolver = DependencyResolver(self.repo)

    def init_project(self, name: Optional[str] = None) -> PackageMetadata:
        """Initialize a new hakai.toml manifest."""
        proj_name = name or os.path.basename(self.project_dir)
        meta = PackageMetadata(
            name=proj_name,
            version="1.0.0",
            description="A modern HAKAI application",
            entry="main.hakai",
        )
        meta.save(self.manifest_path)

        # Create basic entry script if not exists
        entry_file = os.path.join(self.project_dir, meta.entry)
        if not os.path.exists(entry_file):
            with open(entry_file, "w", encoding="utf-8") as f:
                f.write('HAKAI START\nprint("Hello from HAKAI!")\nHAKAI END\n')

        return meta

    def install(self, package_source: Optional[str] = None) -> None:
        """Install a specific package or all manifest dependencies."""
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError("No hakai.toml found in current directory. Run 'hpm init' first.")

        manifest = PackageMetadata.from_toml_file(self.manifest_path)

        if package_source:
            # Install explicit package path or name
            if os.path.isdir(package_source) and os.path.isfile(os.path.join(package_source, "hakai.toml")):
                source_meta = PackageMetadata.from_toml_file(os.path.join(package_source, "hakai.toml"))
                manifest.dependencies[source_meta.name] = source_meta.version
                manifest.save(self.manifest_path)
                self._copy_package(source_meta.name, package_source)
            else:
                found_dir = self.repo.find_package(package_source)
                if not found_dir:
                    raise FileNotFoundError(f"Package '{package_source}' not found.")
                source_meta = PackageMetadata.from_toml_file(os.path.join(found_dir, "hakai.toml"))
                manifest.dependencies[source_meta.name] = source_meta.version
                manifest.save(self.manifest_path)
                self._copy_package(source_meta.name, found_dir)

        # Install all dependencies
        resolved_packages = self.resolver.resolve(manifest)
        lock_entries: Dict[str, dict] = {}

        os.makedirs(self.packages_dir, exist_ok=True)

        for pkg in resolved_packages:
            src = self.repo.find_package(pkg.name)
            if src:
                self._copy_package(pkg.name, src)
                lock_entries[pkg.name] = {
                    "version": pkg.version,
                    "entry": pkg.entry,
                    "checksum": self._compute_checksum(src),
                }

        # Write lockfile
        with open(self.lockfile_path, "w", encoding="utf-8") as f:
            json.dump({"packages": lock_entries}, f, indent=2)

    def uninstall(self, package_name: str) -> bool:
        """Remove package and update manifest and lockfile."""
        if not os.path.exists(self.manifest_path):
            return False

        manifest = PackageMetadata.from_toml_file(self.manifest_path)
        if package_name in manifest.dependencies:
            del manifest.dependencies[package_name]
            manifest.save(self.manifest_path)

        target = os.path.join(self.packages_dir, package_name)
        if os.path.isdir(target):
            shutil.rmtree(target)

        # Update lockfile
        if os.path.exists(self.lockfile_path):
            with open(self.lockfile_path, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
            if package_name in lock_data.get("packages", {}):
                del lock_data["packages"][package_name]
                with open(self.lockfile_path, "w", encoding="utf-8") as f:
                    json.dump(lock_data, f, indent=2)

        return True

    def list_installed(self) -> Dict[str, str]:
        """List all installed packages and versions in .hakai_packages."""
        installed = {}
        if os.path.isdir(self.packages_dir):
            for entry in os.listdir(self.packages_dir):
                pkg_toml = os.path.join(self.packages_dir, entry, "hakai.toml")
                if os.path.isfile(pkg_toml):
                    meta = PackageMetadata.from_toml_file(pkg_toml)
                    installed[meta.name] = meta.version
        return installed

    def _copy_package(self, pkg_name: str, src_dir: str) -> None:
        dest_dir = os.path.join(self.packages_dir, pkg_name)
        if os.path.abspath(src_dir) == os.path.abspath(dest_dir):
            return
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.copytree(src_dir, dest_dir)

    def _compute_checksum(self, dir_path: str) -> str:
        hasher = hashlib.sha256()
        for root, _, files in sorted(os.walk(dir_path)):
            for file in sorted(files):
                fpath = os.path.join(root, file)
                with open(fpath, "rb") as f:
                    hasher.update(f.read())
        return hasher.hexdigest()
