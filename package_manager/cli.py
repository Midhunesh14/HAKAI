"""Command Line Interface for HAKAI Package Manager (hpm)."""

from __future__ import annotations

import argparse
import sys
from package_manager.installer import PackageInstaller
from package_manager.package import PackageMetadata
from package_manager.repository import PackageRepository


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hpm",
        description="HAKAI Package Manager (HPM) 1.0.0",
    )
    subparsers = parser.add_subparsers(dest="command", help="HPM Command")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new HAKAI project manifest")
    init_parser.add_argument("name", nargs="?", default=None, help="Project name")

    # install
    install_parser = subparsers.add_parser("install", help="Install dependencies or a specific package")
    install_parser.add_argument("package", nargs="?", default=None, help="Package name or local directory")

    # uninstall
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("package", help="Package name to uninstall")

    # list
    subparsers.add_parser("list", help="List installed packages")

    # info
    info_parser = subparsers.add_parser("info", help="Display package details")
    info_parser.add_argument("package", help="Package name")

    # search
    search_parser = subparsers.add_parser("search", help="Search available packages")
    search_parser.add_argument("query", help="Keyword to search")

    # update
    subparsers.add_parser("update", help="Update installed dependencies")

    return parser


def main(args=None) -> int:
    parser = create_parser()
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 0

    installer = PackageInstaller()

    if parsed.command == "init":
        meta = installer.init_project(parsed.name)
        print(f"[HPM] Initialized new HAKAI project: {meta.name} (hakai.toml created)")
        return 0

    elif parsed.command == "install":
        try:
            installer.install(parsed.package)
            if parsed.package:
                print(f"[HPM] Successfully installed package: {parsed.package}")
            else:
                print("[HPM] Successfully installed all project dependencies.")
            return 0
        except Exception as e:
            print(f"[HPM Error] {e}", file=sys.stderr)
            return 1

    elif parsed.command == "uninstall":
        success = installer.uninstall(parsed.package)
        if success:
            print(f"[HPM] Uninstalled {parsed.package}")
            return 0
        else:
            print(f"[HPM Error] Failed to uninstall {parsed.package}", file=sys.stderr)
            return 1

    elif parsed.command == "list":
        installed = installer.list_installed()
        if not installed:
            print("[HPM] No packages installed in .hakai_packages/")
        else:
            print("[HPM] Installed packages:")
            for name, ver in installed.items():
                print(f"  * {name} @ {ver}")
        return 0

    elif parsed.command == "info":
        repo = PackageRepository()
        pkg_dir = repo.find_package(parsed.package)
        if pkg_dir:
            import os
            meta = PackageMetadata.from_toml_file(os.path.join(pkg_dir, "hakai.toml"))
            print(f"Package: {meta.name}")
            print(f"Version: {meta.version}")
            print(f"Description: {meta.description}")
            print(f"Entry: {meta.entry}")
            print(f"Author: {meta.author}")
            print(f"License: {meta.license}")
            return 0
        print(f"[HPM Error] Package '{parsed.package}' not found.", file=sys.stderr)
        return 1

    elif parsed.command == "search":
        repo = PackageRepository()
        available = repo.list_available()
        matches = {k: v for k, v in available.items() if parsed.query.lower() in k.lower()}
        if not matches:
            print(f"[HPM] No packages matching '{parsed.query}' found.")
        else:
            print(f"[HPM] Found {len(matches)} package(s):")
            for name, ver in matches.items():
                print(f"  * {name} ({ver})")
        return 0

    elif parsed.command == "update":
        try:
            installer.install()
            print("[HPM] Dependencies updated successfully.")
            return 0
        except Exception as e:
            print(f"[HPM Error] {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

