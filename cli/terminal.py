"""Terminal utilities, formatting, and ASCII branding for HAKAI CLI."""

from __future__ import annotations

import sys

BANNER = """
   _    _          _  __     _____ 
  | |  | |   /\\   | |/ / /\\ |_   _|
  | |__| |  /  \\  | ' / /  \\  | |  
  |  __  | / /\\ \\ |  < / /\\ \\ | |  
  | |  | |/ ____ \\| . \\ ____ \\| |_ 
  |_|  |_/_/    \\_|_|\\_\\    |_/___/  v1.0.0
  The Independent High-Performance Programming Language
"""


def color_text(text: str, color_code: str) -> str:
    """Wrap text in ANSI color codes if stdout is interactive."""
    if sys.stdout.isatty():
        return f"\033[{color_code}m{text}\033[0m"
    return text


def print_banner() -> None:
    print(color_text(BANNER, "36;1"))


def print_success(msg: str) -> None:
    print(color_text(f"[OK] {msg}", "32"))


def print_error(msg: str) -> None:
    print(color_text(f"[ERROR] {msg}", "31;1"), file=sys.stderr)


def print_info(msg: str) -> None:
    print(color_text(f"[INFO] {msg}", "34"))
