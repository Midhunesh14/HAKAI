"""Lexical scope environment for the HAKAI runtime."""

from __future__ import annotations

from typing import Any, Dict, Optional, Set
from compiler.errors import HakaiNameError, HakaiTypeError


class Environment:
    """Manages variable bindings and lexical scopes."""

    def __init__(self, enclosing: Optional[Environment] = None) -> None:
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}
        self.constants: Set[str] = set()

    def define(self, name: str, value: Any, is_const: bool = False) -> None:
        """Define a new variable or constant in the current immediate scope."""
        self.values[name] = value
        if is_const:
            self.constants.add(name)

    def assign(
        self,
        name: str,
        value: Any,
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> None:
        """Assign to an existing variable in this scope or an enclosing scope."""
        if name in self.values:
            if name in self.constants:
                raise HakaiTypeError(
                    message=f"Cannot reassign to constant '{name}'.",
                    filename=filename,
                    line=line,
                    column=column,
                    source_code=source_code,
                    suggestion=f"'{name}' was declared with 'const'. Use 'let' if it needs to change.",
                )
            self.values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(
                name=name,
                value=value,
                filename=filename,
                line=line,
                column=column,
                source_code=source_code,
            )
            return

        raise HakaiNameError(
            message=f"Undefined variable '{name}'.",
            filename=filename,
            line=line,
            column=column,
            source_code=source_code,
            suggestion=f"Declare '{name}' with 'let {name} = ...' before assigning to it.",
        )

    def get(
        self,
        name: str,
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        """Retrieve a variable's value from this scope or an enclosing scope."""
        if name in self.values:
            return self.values[name]

        if self.enclosing is not None:
            return self.enclosing.get(
                name=name,
                filename=filename,
                line=line,
                column=column,
                source_code=source_code,
            )

        raise HakaiNameError(
            message=f"Undefined identifier '{name}'.",
            filename=filename,
            line=line,
            column=column,
            source_code=source_code,
            suggestion=f"Check spelling or define '{name}' before using it.",
        )

