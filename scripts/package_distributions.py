"""Distribution packager and checksum generator for HAKAI releases."""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import zipfile
from typing import Dict, List


VERSION = "1.0.0"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
BIN_DIR = os.path.join(DIST_DIR, "bin")


def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def package_windows_portable() -> str:
    archive_name = f"HAKAI-{VERSION}-Windows-x64-Portable.zip"
    archive_path = os.path.join(DIST_DIR, archive_name)

    print(f"Creating {archive_name}...")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # CLI
        cli_exe = os.path.join(BIN_DIR, "hakai.exe")
        if os.path.isfile(cli_exe):
            zf.write(cli_exe, "bin/hakai.exe")
        # HPM
        hpm_exe = os.path.join(BIN_DIR, "hpm.exe")
        if os.path.isfile(hpm_exe):
            zf.write(hpm_exe, "bin/hpm.exe")
        # Docs and License
        zf.write(os.path.join(ROOT_DIR, "LICENSE"), "LICENSE")
        zf.write(os.path.join(ROOT_DIR, "README.md"), "README.md")
        # Examples
        examples_dir = os.path.join(ROOT_DIR, "examples")
        if os.path.isdir(examples_dir):
            for file in os.listdir(examples_dir):
                if file.endswith((".hakai", ".hbc")):
                    zf.write(os.path.join(examples_dir, file), f"examples/{file}")

    return archive_path


def package_windows_studio() -> str:
    archive_name = f"HAKAI-Studio-{VERSION}-Windows-x64.zip"
    archive_path = os.path.join(DIST_DIR, archive_name)

    print(f"Creating {archive_name}...")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        studio_exe = os.path.join(BIN_DIR, "hakai-studio.exe")
        if os.path.isfile(studio_exe):
            zf.write(studio_exe, "hakai-studio.exe")
        zf.write(os.path.join(ROOT_DIR, "LICENSE"), "LICENSE")
        zf.write(os.path.join(ROOT_DIR, "README.md"), "README.md")

    return archive_path


def create_installer_script() -> str:
    installer_path = os.path.join(DIST_DIR, f"HAKAI-{VERSION}-Windows-Installer.bat")
    content = f"""@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo HAKAI Programming Language {VERSION} Windows Installer
echo ========================================================
echo.

set "TARGET_DIR=%LOCALAPPDATA%\\Programs\\HAKAI"
set "BIN_DIR=%TARGET_DIR%\\bin"

echo Installing HAKAI to: %TARGET_DIR%
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

if exist "bin\\hakai.exe" (
    copy /Y "bin\\hakai.exe" "%BIN_DIR%\\hakai.exe" >nul
)
if exist "bin\\hpm.exe" (
    copy /Y "bin\\hpm.exe" "%BIN_DIR%\\hpm.exe" >nul
)
if exist "hakai-studio.exe" (
    copy /Y "hakai-studio.exe" "%TARGET_DIR%\\hakai-studio.exe" >nul
)

echo Adding %BIN_DIR% to User PATH...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ';%BIN_DIR%', 'User')"

echo.
echo ========================================================
echo HAKAI {VERSION} has been successfully installed!
echo Open a new Command Prompt or Terminal and run:
echo   hakai --version
echo   hakai repl
echo ========================================================
pause
"""
    with open(installer_path, "w", encoding="utf-8") as f:
        f.write(content)
    return installer_path


def generate_checksums() -> str:
    checksums_file = os.path.join(DIST_DIR, "SHA256SUMS.txt")
    lines = []
    print("\nCalculating SHA256 checksums:")
    for root, _, files in os.walk(DIST_DIR):
        for file in sorted(files):
            if file == "SHA256SUMS.txt" or file.startswith(".tmp"):
                continue
            fpath = os.path.join(root, file)
            # Only root dist files
            if os.path.dirname(fpath) == DIST_DIR:
                digest = compute_sha256(fpath)
                line = f"{digest}  {file}"
                lines.append(line)
                print(f"  {file}: {digest}")

    with open(checksums_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return checksums_file


def main() -> int:
    os.makedirs(DIST_DIR, exist_ok=True)
    if os.path.isfile(os.path.join(BIN_DIR, "hakai.exe")):
        package_windows_portable()
    if os.path.isfile(os.path.join(BIN_DIR, "hakai-studio.exe")):
        package_windows_studio()

    create_installer_script()
    generate_checksums()
    print("\nDistribution packaging completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

