"""Lexer (Tokenizer) for the HAKAI programming language."""

from __future__ import annotations

from typing import List, Optional
from compiler.tokens import Token, TokenType, KEYWORDS
from compiler.errors import HakaiLexerError


class Lexer:
    """Converts HAKAI source code into a stream of Token objects."""

    def __init__(self, source: str, filename: str = "<source>") -> None:
        self.source = source
        self.filename = filename
        self.length = len(source)
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.token_start_column = 1

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while not self._is_at_end():
            self.start = self.current
            self.token_start_column = self.column
            token = self._scan_token()
            if token is not None:
                tokens.append(token)

        # Append EOF token
        tokens.append(
            Token(
                kind=TokenType.EOF,
                lexeme="",
                literal=None,
                line=self.line,
                column=self.column,
                source=self.filename,
            )
        )
        return self._post_process_boundaries(tokens)

    def _post_process_boundaries(self, tokens: List[Token]) -> List[Token]:
        """Combine consecutive IDENTIFIER('HAKAI') + IDENTIFIER('START'/'END') into boundary tokens."""
        processed: List[Token] = []
        i = 0
        n = len(tokens)
        while i < n:
            tok = tokens[i]
            if (
                tok.kind == TokenType.IDENTIFIER
                and tok.lexeme == "HAKAI"
                and i + 1 < n
                and tokens[i + 1].kind == TokenType.IDENTIFIER
                and tokens[i + 1].lexeme in ("START", "END")
            ):
                next_tok = tokens[i + 1]
                kind = (
                    TokenType.HAKAI_START
                    if next_tok.lexeme == "START"
                    else TokenType.HAKAI_END
                )
                combined = Token(
                    kind=kind,
                    lexeme=f"HAKAI {next_tok.lexeme}",
                    literal=None,
                    line=tok.line,
                    column=tok.column,
                    source=tok.source,
                )
                processed.append(combined)
                i += 2
                continue
            processed.append(tok)
            i += 1
        return processed

    def _is_at_end(self) -> bool:
        return self.current >= self.length

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        self.column += 1
        return ch

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= self.length:
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def _make_token(self, kind: TokenType, literal: object = None) -> Token:
        lexeme = self.source[self.start : self.current]
        return Token(
            kind=kind,
            lexeme=lexeme,
            literal=literal,
            line=self.line,
            column=self.token_start_column,
            source=self.filename,
        )

    def _scan_token(self) -> Optional[Token]:
        ch = self._advance()

        # Whitespace
        if ch in (" ", "\t", "\r"):
            return None
        if ch == "\n":
            self.line += 1
            self.column = 1
            return None

        # Punctuation & Delimiters
        if ch == "(":
            return self._make_token(TokenType.LEFT_PAREN)
        if ch == ")":
            return self._make_token(TokenType.RIGHT_PAREN)
        if ch == "{":
            return self._make_token(TokenType.LEFT_BRACE)
        if ch == "}":
            return self._make_token(TokenType.RIGHT_BRACE)
        if ch == "[":
            return self._make_token(TokenType.LEFT_BRACKET)
        if ch == "]":
            return self._make_token(TokenType.RIGHT_BRACKET)
        if ch == ",":
            return self._make_token(TokenType.COMMA)
        if ch == ";":
            return self._make_token(TokenType.SEMICOLON)
        if ch == ":":
            return self._make_token(TokenType.COLON)
        if ch == ".":
            return self._make_token(TokenType.DOT)

        # Operators
        if ch == "+":
            return self._make_token(TokenType.PLUS)
        if ch == "-":
            if self._match(">"):
                return self._make_token(TokenType.ARROW)
            return self._make_token(TokenType.MINUS)
        if ch == "*":
            if self._match("*"):
                return self._make_token(TokenType.STAR_STAR)
            return self._make_token(TokenType.STAR)
        if ch == "/":
            if self._match("/"):
                # Single line comment
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
                return None
            elif self._match("*"):
                # Multi-line comment
                self._block_comment()
                return None
            return self._make_token(TokenType.SLASH)
        if ch == "%":
            return self._make_token(TokenType.PERCENT)
        if ch == "!":
            if self._match("="):
                return self._make_token(TokenType.BANG_EQUAL)
            return self._make_token(TokenType.BANG)
        if ch == "=":
            if self._match("="):
                return self._make_token(TokenType.EQUAL_EQUAL)
            return self._make_token(TokenType.EQUAL)
        if ch == "<":
            if self._match("="):
                return self._make_token(TokenType.LESS_EQUAL)
            if self._match("<"):
                return self._make_token(TokenType.LEFT_SHIFT)
            return self._make_token(TokenType.LESS)
        if ch == ">":
            if self._match("="):
                return self._make_token(TokenType.GREATER_EQUAL)
            if self._match(">"):
                return self._make_token(TokenType.RIGHT_SHIFT)
            return self._make_token(TokenType.GREATER)
        if ch == "&":
            if self._match("&"):
                return self._make_token(TokenType.AND)
            return self._make_token(TokenType.AMPERSAND)
        if ch == "|":
            if self._match("|"):
                return self._make_token(TokenType.OR)
            return self._make_token(TokenType.PIPE)
        if ch == "^":
            return self._make_token(TokenType.CARET)
        if ch == "~":
            return self._make_token(TokenType.TILDE)

        # String literals
        if ch in ('"', "'"):
            return self._string(ch)

        # Number literals
        if ch.isdigit():
            return self._number()

        # Identifiers and keywords
        if ch.isalpha() or ch == "_":
            return self._identifier()

        raise HakaiLexerError(
            message=f"Unexpected character: {ch!r}",
            filename=self.filename,
            line=self.line,
            column=self.token_start_column,
            source_code=self.source,
            suggestion="Remove or replace this character.",
        )

    def _block_comment(self) -> None:
        start_line = self.line
        start_col = self.token_start_column
        while not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
                self.column = 1
                self._advance()
            elif self._peek() == "*" and self._peek_next() == "/":
                self._advance()  # *
                self._advance()  # /
                return
            else:
                self._advance()

        raise HakaiLexerError(
            message="Unterminated multi-line comment.",
            filename=self.filename,
            line=start_line,
            column=start_col,
            source_code=self.source,
            suggestion="Close comment with '*/'.",
        )

    def _string(self, quote_char: str) -> Token:
        chars: List[str] = []
        start_line = self.line
        start_col = self.token_start_column

        while not self._is_at_end() and self._peek() != quote_char:
            ch = self._advance()
            if ch == "\n":
                self.line += 1
                self.column = 1
                chars.append("\n")
            elif ch == "\\":
                if self._is_at_end():
                    break
                escape_ch = self._advance()
                if escape_ch == "n":
                    chars.append("\n")
                elif escape_ch == "t":
                    chars.append("\t")
                elif escape_ch == "r":
                    chars.append("\r")
                elif escape_ch == "\\":
                    chars.append("\\")
                elif escape_ch == quote_char:
                    chars.append(quote_char)
                else:
                    chars.append(escape_ch)
            else:
                chars.append(ch)

        if self._is_at_end():
            raise HakaiLexerError(
                message=f"Unterminated string literal.",
                filename=self.filename,
                line=start_line,
                column=start_col,
                source_code=self.source,
                suggestion=f"Add closing {quote_char} to terminate the string.",
            )

        self._advance()  # Consume closing quote
        literal_str = "".join(chars)
        return self._make_token(TokenType.STRING, literal=literal_str)

    def _number(self) -> Token:
        while self._peek().isdigit():
            self._advance()

        is_float = False
        # Check for fractional part
        if self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            self._advance()  # consume '.'
            while self._peek().isdigit():
                self._advance()

        # Scientific notation (e.g. 1e-4)
        if self._peek() in ("e", "E"):
            next_ch = self._peek_next()
            if next_ch.isdigit() or next_ch in ("+", "-"):
                is_float = True
                self._advance()  # e
                if self._peek() in ("+", "-"):
                    self._advance()
                while self._peek().isdigit():
                    self._advance()

        lexeme = self.source[self.start : self.current]
        if is_float:
            return self._make_token(TokenType.FLOAT, literal=float(lexeme))
        return self._make_token(TokenType.INTEGER, literal=int(lexeme))

    def _identifier(self) -> Token:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        lexeme = self.source[self.start : self.current]
        kind = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)

        literal: object = None
        if kind == TokenType.TRUE:
            kind = TokenType.BOOLEAN
            literal = True
        elif kind == TokenType.FALSE:
            kind = TokenType.BOOLEAN
            literal = False
        elif kind == TokenType.NULL_KW:
            kind = TokenType.NULL
            literal = None

        return self._make_token(kind, literal=literal)

