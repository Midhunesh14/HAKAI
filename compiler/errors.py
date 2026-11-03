"""Diagnostic error reporting for the HAKAI compiler and runtime."""

from __future__ import annotations
from typing import Optional


class HakaiError(Exception):
    """Base class for all HAKAI exceptions and errors."""

    def __init__(
        self,
        message: str,
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column
        self.source_code = source_code
        self.suggestion = suggestion

    def format(self) -> str:
        error_name = self.__class__.__name__
        if error_name.startswith("Hakai"):
            error_name = error_name[5:]  # e.g., SyntaxError instead of HakaiSyntaxError
        
        header = f"HAKAI {error_name}:"
        loc = f"  {self.filename}:{self.line}:{self.column}"
        msg = f"  {self.message}"

        lines = [header, loc, msg]

        if self.source_code:
            code_lines = self.source_code.splitlines()
            if 1 <= self.line <= len(code_lines):
                line_text = code_lines[self.line - 1]
                lines.append("")
                lines.append(f"    {line_text}")
                pointer = " " * (self.column - 1) + "^"
                lines.append(f"    {pointer}")

        if self.suggestion:
            lines.append(f"  Note: {self.suggestion}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.format()


class HakaiLexerError(HakaiError):
    """Raised when an invalid token or character sequence is encountered."""


class HakaiSyntaxError(HakaiError):
    """Raised when parsing fails due to grammatical violations."""


class HakaiSemanticError(HakaiError):
    """Raised during static analysis (e.g. constant reassignment, undefined variables)."""


class HakaiRuntimeError(HakaiError):
    """Raised during runtime execution in the interpreter or VM."""


class HakaiTypeError(HakaiRuntimeError):
    """Raised on invalid type operations or conversions."""


class HakaiNameError(HakaiRuntimeError):
    """Raised when an identifier is not bound in the current scope."""


class HakaiIndexError(HakaiRuntimeError):
    """Raised when array index is out of bounds."""


class HakaiKeyError(HakaiRuntimeError):
    """Raised when map key is not found."""


class HakaiImportError(HakaiRuntimeError):
    """Raised when a module cannot be resolved or loaded."""


class HakaiReturnSignal(Exception):
    """Control flow signal for function returns."""

    def __init__(self, value: object) -> None:
        self.value = value


class HakaiBreakSignal(Exception):
    """Control flow signal for break statement."""


class HakaiContinueSignal(Exception):
    """Control flow signal for continue statement."""

