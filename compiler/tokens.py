"""Token types for the HAKAI language.

Every token carries:
  * its kind (an enum member),
  * its literal value (for numbers, identifiers, strings),
  * the source location (file, line, column),
  * the original source text (for diagnostics).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional


class TokenType(Enum):
    """Every distinct token the HAKAI lexer can produce."""

    # Program boundaries
    HAKAI_START = auto()
    HAKAI_END = auto()

    # Punctuation / delimiters
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    DOT = auto()
    COLON = auto()
    ARROW = auto()  # -> used in some constructs

    # Literals
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()

    # Keywords
    LET = auto()
    CONST = auto()
    IF = auto()
    ELSE = auto()
    ELSEIF = auto()
    WHILE = auto()
    REPEAT = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    FUNCTION = auto()
    CLASS = auto()
    EXTENDS = auto()
    STATIC = auto()
    SELF = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    EXPORT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    IN = auto()
    IS = auto()
    TRUE = auto()
    FALSE = auto()
    NULL_KW = auto()
    NEW = auto()
    SUPER = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    FOR = auto()
    FOREACH = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    STAR_STAR = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    AMPERSAND = auto()
    PIPE = auto()
    CARET = auto()
    TILDE = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()

    # Misc
    EOF = auto()
    UNKNOWN = auto()


KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elseif": TokenType.ELSEIF,
    "while": TokenType.WHILE,
    "repeat": TokenType.REPEAT,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "return": TokenType.RETURN,
    "function": TokenType.FUNCTION,
    "class": TokenType.CLASS,
    "extends": TokenType.EXTENDS,
    "static": TokenType.STATIC,
    "self": TokenType.SELF,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "as": TokenType.AS,
    "export": TokenType.EXPORT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "in": TokenType.IN,
    "is": TokenType.IS,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL_KW,
    "new": TokenType.NEW,
    "super": TokenType.SUPER,
    "try": TokenType.TRY,
    "catch": TokenType.CATCH,
    "finally": TokenType.FINALLY,
    "throw": TokenType.THROW,
    "for": TokenType.FOR,
    "foreach": TokenType.FOREACH,
}


@dataclass
class Token:
    """A single lexical token."""

    kind: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int
    source: str = ""

    def __post_init__(self) -> None:
        if self.kind in (TokenType.EOF, TokenType.UNKNOWN):
            self.lexeme = self.lexeme or ""

    @property
    def is_keyword(self) -> bool:
        return self.kind in KEYWORDS.values()

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        if self.literal is not None:
            return f"Token({self.kind.name}, {self.lexeme!r}, {self.literal!r}, {self.line}:{self.column})"
        return f"Token({self.kind.name}, {self.lexeme!r}, {self.line}:{self.column})"