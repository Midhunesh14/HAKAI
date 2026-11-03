"""Standard Library, Builtins, and Runtime Environment for HAKAI."""

from __future__ import annotations

import io
import math
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional
from compiler.errors import HakaiImportError, HakaiTypeError, HakaiRuntimeError
from interpreter.values import (
    HakaiBuiltinFunction,
    hakai_to_str,
    hakai_type_name,
    is_truthy,
)


class HakaiFileHandle:
    """Safe file wrapper for HAKAI scripts."""

    def __init__(self, path: str, mode: str) -> None:
        self.path = path
        self.mode = mode
        self._file = open(path, mode, encoding="utf-8")
        self.is_closed = False

    def read(self) -> str:
        if self.is_closed:
            raise HakaiRuntimeError("Cannot read from a closed file.")
        return self._file.read()

    def write(self, content: str) -> int:
        if self.is_closed:
            raise HakaiRuntimeError("Cannot write to a closed file.")
        return self._file.write(str(content))

    def close(self) -> None:
        if not self.is_closed:
            self._file.close()
            self.is_closed = True

    def get_method(self, name: str) -> HakaiBuiltinFunction:
        if name == "read":
            return HakaiBuiltinFunction("read", lambda interp: self.read(), 0, 0)
        if name == "write":
            return HakaiBuiltinFunction("write", lambda interp, text: self.write(text), 1, 1)
        if name == "close":
            return HakaiBuiltinFunction("close", lambda interp: self.close(), 0, 0)
        raise HakaiRuntimeError(f"File object has no method '{name}'.")

    def __hakai_str__(self) -> str:
        return f"<file '{self.path}' mode='{self.mode}'>"


class RuntimeContext:
    """Encapsulates IO streams, standard libraries, and module loading."""

    def __init__(
        self,
        stdout: Optional[io.TextIOBase] = None,
        stdin: Optional[io.TextIOBase] = None,
    ) -> None:
        self.stdout = stdout or sys.stdout
        self.stdin = stdin or sys.stdin
        self.modules: Dict[str, Dict[str, Any]] = {}
        self._init_standard_library()

    def print(self, *args: Any) -> None:
        text = " ".join(hakai_to_str(a) for a in args)
        self.stdout.write(text + "\n")
        self.stdout.flush()

    def _init_standard_library(self) -> None:
        # Math module
        self.modules["math"] = {
            "pi": math.pi,
            "e": math.e,
            "sqrt": HakaiBuiltinFunction("sqrt", lambda interp, x: math.sqrt(x), 1, 1),
            "pow": HakaiBuiltinFunction("pow", lambda interp, x, y: math.pow(x, y), 2, 2),
            "abs": HakaiBuiltinFunction("abs", lambda interp, x: abs(x), 1, 1),
            "floor": HakaiBuiltinFunction("floor", lambda interp, x: math.floor(x), 1, 1),
            "ceil": HakaiBuiltinFunction("ceil", lambda interp, x: math.ceil(x), 1, 1),
            "round": HakaiBuiltinFunction("round", lambda interp, x: round(x), 1, 1),
            "sin": HakaiBuiltinFunction("sin", lambda interp, x: math.sin(x), 1, 1),
            "cos": HakaiBuiltinFunction("cos", lambda interp, x: math.cos(x), 1, 1),
            "tan": HakaiBuiltinFunction("tan", lambda interp, x: math.tan(x), 1, 1),
        }

        # Strings module
        self.modules["strings"] = {
            "upper": HakaiBuiltinFunction("upper", lambda interp, s: str(s).upper(), 1, 1),
            "lower": HakaiBuiltinFunction("lower", lambda interp, s: str(s).lower(), 1, 1),
            "trim": HakaiBuiltinFunction("trim", lambda interp, s: str(s).strip(), 1, 1),
            "split": HakaiBuiltinFunction("split", lambda interp, s, d=" ": str(s).split(d), 1, 2),
            "join": HakaiBuiltinFunction("join", lambda interp, arr, d="": d.join(hakai_to_str(x) for x in arr), 1, 2),
            "contains": HakaiBuiltinFunction("contains", lambda interp, s, sub: str(sub) in str(s), 2, 2),
            "replace": HakaiBuiltinFunction("replace", lambda interp, s, old, new: str(s).replace(str(old), str(new)), 3, 3),
            "starts_with": HakaiBuiltinFunction("starts_with", lambda interp, s, p: str(s).startswith(str(p)), 2, 2),
            "ends_with": HakaiBuiltinFunction("ends_with", lambda interp, s, p: str(s).endswith(str(p)), 2, 2),
            "len": HakaiBuiltinFunction("len", lambda interp, s: len(str(s)), 1, 1),
        }

        # Collections module
        def _col_push(interp: Any, arr: list, item: Any) -> list:
            if not isinstance(arr, list):
                raise HakaiTypeError("collections.push expects an Array as first argument.")
            arr.append(item)
            return arr

        def _col_pop(interp: Any, arr: list) -> Any:
            if not isinstance(arr, list):
                raise HakaiTypeError("collections.pop expects an Array.")
            if not arr:
                raise HakaiRuntimeError("Cannot pop from an empty Array.")
            return arr.pop()

        self.modules["collections"] = {
            "push": HakaiBuiltinFunction("push", _col_push, 2, 2),
            "pop": HakaiBuiltinFunction("pop", _col_pop, 1, 1),
            "length": HakaiBuiltinFunction("length", lambda interp, x: len(x), 1, 1),
            "keys": HakaiBuiltinFunction("keys", lambda interp, m: list(m.keys()), 1, 1),
            "values": HakaiBuiltinFunction("values", lambda interp, m: list(m.values()), 1, 1),
            "has_key": HakaiBuiltinFunction("has_key", lambda interp, m, k: k in m, 2, 2),
        }

        # Files module
        def _read_text(interp: Any, path: str) -> str:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        def _write_text(interp: Any, path: str, content: str) -> int:
            with open(path, "w", encoding="utf-8") as f:
                return f.write(str(content))

        def _append_text(interp: Any, path: str, content: str) -> int:
            with open(path, "a", encoding="utf-8") as f:
                return f.write(str(content))

        self.modules["files"] = {
            "read_text": HakaiBuiltinFunction("read_text", _read_text, 1, 1),
            "write_text": HakaiBuiltinFunction("write_text", _write_text, 2, 2),
            "append_text": HakaiBuiltinFunction("append_text", _append_text, 2, 2),
            "exists": HakaiBuiltinFunction("exists", lambda interp, p: os.path.exists(p), 1, 1),
            "delete": HakaiBuiltinFunction("delete", lambda interp, p: os.remove(p), 1, 1),
            "open": HakaiBuiltinFunction("open", lambda interp, p, m="r": HakaiFileHandle(p, m), 1, 2),
        }

        # IO module
        self.modules["io"] = {
            "print": HakaiBuiltinFunction("print", lambda interp, *args: self.print(*args), 0, 255),
            "println": HakaiBuiltinFunction("println", lambda interp, *args: self.print(*args), 0, 255),
            "input": HakaiBuiltinFunction("input", lambda interp, prompt="": input(prompt), 0, 1),
        }

        # System module
        self.modules["system"] = {
            "time": HakaiBuiltinFunction("time", lambda interp: time.time(), 0, 0),
            "sleep": HakaiBuiltinFunction("sleep", lambda interp, s: time.sleep(s), 1, 1),
            "platform": HakaiBuiltinFunction("platform", lambda interp: sys.platform, 0, 0),
            "version": HakaiBuiltinFunction("version", lambda interp: "1.0.0", 0, 0),
            "args": HakaiBuiltinFunction("args", lambda interp: sys.argv[1:], 0, 0),
            "exit": HakaiBuiltinFunction("exit", lambda interp, code=0: sys.exit(int(code)), 0, 1),
        }

    def get_builtins(self) -> Dict[str, Any]:
        """Return global builtin functions available in every HAKAI scope."""
        def _builtin_len(interp: Any, arg: Any) -> int:
            if hasattr(arg, "__len__"):
                return len(arg)
            raise HakaiTypeError(f"len() not supported on type {hakai_type_name(arg)}.")

        def _builtin_range(interp: Any, *args: Any) -> list:
            if len(args) == 1:
                return list(range(int(args[0])))
            elif len(args) == 2:
                return list(range(int(args[0]), int(args[1])))
            elif len(args) == 3:
                return list(range(int(args[0]), int(args[1]), int(args[2])))
            raise HakaiTypeError("range() takes 1, 2, or 3 arguments.")

        return {
            "print": HakaiBuiltinFunction("print", lambda interp, *a: self.print(*a), 0, 255),
            "println": HakaiBuiltinFunction("println", lambda interp, *a: self.print(*a), 0, 255),
            "type": HakaiBuiltinFunction("type", lambda interp, x: hakai_type_name(x), 1, 1),
            "len": HakaiBuiltinFunction("len", _builtin_len, 1, 1),
            "str": HakaiBuiltinFunction("str", lambda interp, x: hakai_to_str(x), 1, 1),
            "int": HakaiBuiltinFunction("int", lambda interp, x: int(x), 1, 1),
            "float": HakaiBuiltinFunction("float", lambda interp, x: float(x), 1, 1),
            "bool": HakaiBuiltinFunction("bool", lambda interp, x: is_truthy(x), 1, 1),
            "range": HakaiBuiltinFunction("range", _builtin_range, 1, 3),
            "open": HakaiBuiltinFunction("open", lambda interp, p, m="r": HakaiFileHandle(p, m), 1, 2),
        }

    def load_module(self, name: str, current_dir: str = ".") -> Dict[str, Any]:
        if name in self.modules:
            return self.modules[name]

        # Look for local .hakai file
        local_path = os.path.join(current_dir, f"{name}.hakai")
        if os.path.isfile(local_path):
            from compiler.lexer import Lexer
            from compiler.parser import Parser
            from interpreter.interpreter import Interpreter

            with open(local_path, "r", encoding="utf-8") as f:
                code = f.read()

            tokens = Lexer(code, filename=local_path).tokenize()
            program = Parser(tokens, source_code=code).parse()

            sub_interp = Interpreter(runtime_context=self, base_dir=os.path.dirname(local_path))
            sub_interp.interpret(program)

            # Export user variables and functions
            exported = dict(sub_interp.environment.values)
            self.modules[name] = exported
            return exported

        raise HakaiImportError(f"Module '{name}' not found.")
