"""Memory, Call Stack, and Execution Frames for HAKAI Virtual Machine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from virtual_machine.instructions import HakaiCodeObject
from compiler.errors import HakaiRuntimeError


class Frame:
    """An execution frame representing a single function or script invocation."""

    def __init__(
        self,
        code: HakaiCodeObject,
        globals_dict: Dict[str, Any],
        locals_dict: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.globals = globals_dict
        self.locals = locals_dict if locals_dict is not None else {}
        self.ip = 0  # Instruction pointer
        self.stack: List[Any] = []

    def push(self, val: Any) -> None:
        self.stack.append(val)

    def pop(self) -> Any:
        if not self.stack:
            raise HakaiRuntimeError(f"Stack underflow in frame {self.code.name}.")
        return self.stack.pop()

    def peek(self) -> Any:
        if not self.stack:
            raise HakaiRuntimeError(f"Stack underflow in frame {self.code.name}.")
        return self.stack[-1]


class CallStack:
    """Manages nested execution frames with stack overflow protection."""

    MAX_DEPTH = 1000

    def __init__(self) -> None:
        self.frames: List[Frame] = []

    def push(self, frame: Frame) -> None:
        if len(self.frames) >= self.MAX_DEPTH:
            raise HakaiRuntimeError(
                f"Maximum call stack depth ({self.MAX_DEPTH}) exceeded (Infinite recursion detected)."
            )
        self.frames.append(frame)

    def pop(self) -> Frame:
        if not self.frames:
            raise HakaiRuntimeError("Call stack underflow.")
        return self.frames.pop()

    def current(self) -> Frame:
        if not self.frames:
            raise HakaiRuntimeError("No active frame on call stack.")
        return self.frames[-1]

    def is_empty(self) -> bool:
        return len(self.frames) == 0
