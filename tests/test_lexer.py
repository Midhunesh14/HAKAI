"""Tests for HAKAI Lexer."""

import pytest
from compiler.lexer import Lexer
from compiler.tokens import TokenType
from compiler.errors import HakaiLexerError


def test_program_boundaries():
    source = "HAKAI START\nprint(42)\nHAKAI END"
    tokens = Lexer(source).tokenize()
    assert tokens[0].kind == TokenType.HAKAI_START
    assert tokens[1].kind == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "print"
    assert tokens[2].kind == TokenType.LEFT_PAREN
    assert tokens[3].kind == TokenType.INTEGER
    assert tokens[3].literal == 42
    assert tokens[4].kind == TokenType.RIGHT_PAREN
    assert tokens[5].kind == TokenType.HAKAI_END
    assert tokens[6].kind == TokenType.EOF


def test_literals_and_keywords():
    source = 'let x = 123 let y = 45.67 let s = "hello\\nworld" let b = true let n = null'
    tokens = Lexer(source).tokenize()
    kinds = [t.kind for t in tokens if t.kind != TokenType.EOF]
    assert kinds == [
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.INTEGER,
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.FLOAT,
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.STRING,
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.BOOLEAN,
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NULL,
    ]
    str_token = [t for t in tokens if t.kind == TokenType.STRING][0]
    assert str_token.literal == "hello\nworld"


def test_operators():
    source = "+ - * / % ** == != < > <= >= and or not"
    tokens = Lexer(source).tokenize()
    kinds = [t.kind for t in tokens if t.kind != TokenType.EOF]
    assert kinds == [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
        TokenType.STAR_STAR,
        TokenType.EQUAL_EQUAL,
        TokenType.BANG_EQUAL,
        TokenType.LESS,
        TokenType.GREATER,
        TokenType.LESS_EQUAL,
        TokenType.GREATER_EQUAL,
        TokenType.AND,
        TokenType.OR,
        TokenType.NOT,
    ]


def test_comments():
    source = """
    // Single line
    let a = 1
    /* Multi
       line
       comment */
    let b = 2
    """
    tokens = Lexer(source).tokenize()
    non_eof = [t for t in tokens if t.kind != TokenType.EOF]
    assert len(non_eof) == 8  # let a = 1 let b = 2


def test_unterminated_string_raises():
    source = 'let s = "unterminated'
    with pytest.raises(HakaiLexerError) as exc_info:
        Lexer(source).tokenize()
    assert "Unterminated string" in str(exc_info.value)


def test_invalid_character_raises():
    source = "let @ = 10"
    with pytest.raises(HakaiLexerError) as exc_info:
        Lexer(source).tokenize()
    assert "Unexpected character" in str(exc_info.value)

