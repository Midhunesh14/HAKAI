"""HAKAI Virtual Machine (HVM) main entrypoint."""

from __future__ import annotations

import io
import sys
from typing import Any, Dict, Optional
from interpreter.runtime import RuntimeContext
from virtual_machine.execution import ExecutionEngine
from virtual_machine.instructions import HakaiCodeObject
from virtual_machine.memory import CallStack, Frame


class VirtualMachine:
    """Stack-based Virtual Machine for executing compiled HAKAI bytecode."""

    def __init__(
        self,
        stdout: Optional[io.TextIOBase] = None,
        runtime_context: Optional[RuntimeContext] = None,
    ) -> None:
        self.stdout = stdout or sys.stdout
        self.runtime_context = runtime_context or RuntimeContext(stdout=self.stdout)
        self.builtins: Dict[str, Any] = self.runtime_context.get_builtins()
        self.globals: Dict[str, Any] = {}
        self.call_stack = CallStack()
        self.engine = ExecutionEngine(self, self.call_stack)
        self.last_result: Any = None

    def run(self, code: HakaiCodeObject) -> Any:
        """Execute a compiled code object in the VM."""
        initial_frame = Frame(code, self.globals)
        self.call_stack.push(initial_frame)

        while self.engine.step():
            pass

        return self.last_result

    def run_file(self, bytecode_path: str) -> Any:
        """Read and execute a .hbc bytecode file."""
        with open(bytecode_path, "rb") as f:
            data = f.read()
        code_obj = HakaiCodeObject.deserialize(data)
        return self.run(code_obj)
