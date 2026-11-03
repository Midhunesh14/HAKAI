"""Tests for HAKAI Parser and AST representation."""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ast_nodes import (
    Program,
    VarDecl,
    IfStmt,
    WhileStmt,
    RepeatStmt,
    FunctionDecl,
    ClassDecl,
    Binary,
    Literal,
    Identifier,
    ArrayLiteral,
    MapLiteral,
)
from compiler.errors import HakaiSyntaxError


def parse_source(source: str) -> Program:
    tokens = Lexer(source).tokenize()
    return Parser(tokens, source_code=source).parse()


def test_program_boundaries():
    source = """
    HAKAI START
    let x = 10
    print(x)
    HAKAI END
    """
    program = parse_source(source)
    assert program.has_boundaries is True
    assert len(program.statements) == 2


def test_operator_precedence():
    source = "let result = 10 + 20 * 2"
    program = parse_source(source)
    var_decl = program.statements[0]
    assert isinstance(var_decl, VarDecl)
    init = var_decl.initializer
    assert isinstance(init, Binary)
    assert init.operator == "+"
    assert isinstance(init.left, Literal)
    assert init.left.value == 10
    assert isinstance(init.right, Binary)
    assert init.right.operator == "*"
    assert init.right.left.value == 20
    assert init.right.right.value == 2


def test_if_else_if_else():
    source = """
    if age >= 18 {
        print("adult")
    } else if age >= 13 {
        print("teen")
    } else {
        print("child")
    }
    """
    program = parse_source(source)
    stmt = program.statements[0]
    assert isinstance(stmt, IfStmt)
    assert stmt.else_branch is not None
    assert isinstance(stmt.else_branch, IfStmt)


def test_loops():
    source = """
    repeat 5 {
        print("hakai")
    }
    while x < 10 {
        x = x + 1
    }
    """
    program = parse_source(source)
    assert isinstance(program.statements[0], RepeatStmt)
    assert isinstance(program.statements[1], WhileStmt)


def test_functions():
    source = """
    function add(a, b = 5) {
        return a + b
    }
    """
    program = parse_source(source)
    fn = program.statements[0]
    assert isinstance(fn, FunctionDecl)
    assert fn.name == "add"
    assert len(fn.params) == 2
    assert fn.params[1].default_value is not None


def test_class_declaration():
    source = """
    class Dog extends Animal {
        function init(name) {
            self.name = name
        }
        function bark() {
            print("Woof")
        }
    }
    """
    program = parse_source(source)
    cls = program.statements[0]
    assert isinstance(cls, ClassDecl)
    assert cls.name == "Dog"
    assert cls.superclass == "Animal"
    assert len(cls.methods) == 2


def test_collections_parsing():
    source = """
    let arr = [1, 2, 3]
    let m = {"a": 10, "b": 20}
    """
    program = parse_source(source)
    assert isinstance(program.statements[0].initializer, ArrayLiteral)
    assert isinstance(program.statements[1].initializer, MapLiteral)


def test_parser_syntax_error():
    source = "let x = ;"
    with pytest.raises(HakaiSyntaxError) as exc_info:
        parse_source(source)
    assert "Expected an expression" in str(exc_info.value)

