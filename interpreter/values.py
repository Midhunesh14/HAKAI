"""Runtime value representations and builtins for HAKAI."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple
from compiler.errors import HakaiTypeError


def is_truthy(value: Any) -> bool:
    """Determine truthiness of a HAKAI value."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return True


def hakai_type_name(value: Any) -> str:
    """Return friendly type name for diagnostics."""
    if value is None:
        return "Null"
    if isinstance(value, bool):
        return "Boolean"
    if isinstance(value, int):
        return "Integer"
    if isinstance(value, float):
        return "Float"
    if isinstance(value, str):
        return "String"
    if isinstance(value, list):
        return "Array"
    if isinstance(value, tuple):
        return "Tuple"
    if isinstance(value, dict):
        return "Map"
    if hasattr(value, "type_name"):
        return value.type_name
    return type(value).__name__


def hakai_to_str(value: Any) -> str:
    """Format value for printing or string conversion."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        inner = ", ".join(hakai_to_str(x) for x in value)
        return f"[{inner}]"
    if isinstance(value, tuple):
        inner = ", ".join(hakai_to_str(x) for x in value)
        return f"({inner})"
    if isinstance(value, dict):
        inner = ", ".join(f"{hakai_to_str(k)}: {hakai_to_str(v)}" for k, v in value.items())
        return f"{{{inner}}}"
    if hasattr(value, "__hakai_str__"):
        return value.__hakai_str__()
    return str(value)


class HakaiCallable:
    """Abstract interface for callable objects in HAKAI."""

    @property
    def type_name(self) -> str:
        return "Function"

    def arity(self) -> Tuple[int, int]:
        """Return (min_args, max_args)."""
        raise NotImplementedError

    def call(
        self,
        interpreter: Any,
        arguments: List[Any],
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        raise NotImplementedError


class HakaiBuiltinFunction(HakaiCallable):
    """Native built-in function callable."""

    def __init__(
        self,
        name: str,
        fn: Callable[..., Any],
        min_args: int = 0,
        max_args: int = 255,
    ) -> None:
        self.name = name
        self.fn = fn
        self.min_args = min_args
        self.max_args = max_args

    def arity(self) -> Tuple[int, int]:
        return (self.min_args, self.max_args)

    def call(
        self,
        interpreter: Any,
        arguments: List[Any],
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        if len(arguments) < self.min_args or len(arguments) > self.max_args:
            raise HakaiTypeError(
                message=f"Function '{self.name}' expects between {self.min_args} and {self.max_args} arguments, but got {len(arguments)}.",
                filename=filename,
                line=line,
                column=column,
                source_code=source_code,
            )
        try:
            return self.fn(interpreter, *arguments)
        except HakaiTypeError:
            raise
        except Exception as err:
            raise HakaiTypeError(
                message=f"Error in '{self.name}': {err}",
                filename=filename,
                line=line,
                column=column,
                source_code=source_code,
            )

    def __hakai_str__(self) -> str:
        return f"<builtin function {self.name}>"

    def __repr__(self) -> str:
        return self.__hakai_str__()
