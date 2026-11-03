"""Intermediate Representation (IR) for HAKAI Compiler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class IRInstruction:
    """Base Three-Address / Linear IR instruction."""
    op: str
    dest: Optional[str] = None
    src1: Optional[Any] = None
    src2: Optional[Any] = None
    line: int = 1


@dataclass
class IRBlock:
    """Basic block of IR instructions."""
    label: str
    instructions: List[IRInstruction]


@dataclass
class IRProgram:
    """Complete lowered IR representation of a HAKAI compilation unit."""
    blocks: List[IRBlock]
    constants: List[Any]
    globals: List[str]
