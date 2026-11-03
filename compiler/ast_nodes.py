"""Abstract Syntax Tree (AST) node definitions for HAKAI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


@dataclass
class ASTNode:
    """Base class for all AST nodes with source position."""

    line: int = 1
    column: int = 1
    filename: str = "<source>"

    def accept(self, visitor: "ASTVisitor") -> Any:
        method_name = f"visit_{self.__class__.__name__}"
        visitor_fn = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_fn(self)


# ============================================================================
# Expressions
# ============================================================================

@dataclass
class Expr(ASTNode):
    """Base class for expression nodes."""


@dataclass
class Literal(Expr):
    value: Any = None


@dataclass
class Identifier(Expr):
    name: str = ""


@dataclass
class Binary(Expr):
    left: Expr = field(default_factory=Expr)
    operator: str = ""
    right: Expr = field(default_factory=Expr)


@dataclass
class Unary(Expr):
    operator: str = ""
    operand: Expr = field(default_factory=Expr)


@dataclass
class Assign(Expr):
    name: str = ""
    value: Expr = field(default_factory=Expr)


@dataclass
class Call(Expr):
    callee: Expr = field(default_factory=Expr)
    arguments: List[Expr] = field(default_factory=list)


@dataclass
class Get(Expr):
    """Member access: object.property"""
    obj: Expr = field(default_factory=Expr)
    name: str = ""


@dataclass
class Set(Expr):
    """Member assignment: object.property = value"""
    obj: Expr = field(default_factory=Expr)
    name: str = ""
    value: Expr = field(default_factory=Expr)


@dataclass
class Index(Expr):
    """Subscript access: target[index]"""
    target: Expr = field(default_factory=Expr)
    index: Expr = field(default_factory=Expr)


@dataclass
class IndexSet(Expr):
    """Subscript assignment: target[index] = value"""
    target: Expr = field(default_factory=Expr)
    index: Expr = field(default_factory=Expr)
    value: Expr = field(default_factory=Expr)


@dataclass
class ArrayLiteral(Expr):
    elements: List[Expr] = field(default_factory=list)


@dataclass
class MapLiteral(Expr):
    pairs: List[Tuple[Expr, Expr]] = field(default_factory=list)


@dataclass
class TupleLiteral(Expr):
    elements: List[Expr] = field(default_factory=list)


@dataclass
class SelfNode(Expr):
    """Reference to 'self' inside methods."""


@dataclass
class SuperNode(Expr):
    """Super method access: super.method"""
    method: str = ""


# ============================================================================
# Statements
# ============================================================================

@dataclass
class Stmt(ASTNode):
    """Base class for statement nodes."""


@dataclass
class ExpressionStmt(Stmt):
    expression: Expr = field(default_factory=Expr)


@dataclass
class VarDecl(Stmt):
    name: str = ""
    initializer: Optional[Expr] = None
    is_const: bool = False


@dataclass
class Parameter:
    name: str
    default_value: Optional[Expr] = None


@dataclass
class Block(Stmt):
    statements: List[Stmt] = field(default_factory=list)


@dataclass
class FunctionDecl(Stmt):
    name: str = ""
    params: List[Parameter] = field(default_factory=list)
    body: Block = field(default_factory=Block)
    is_static: bool = False


@dataclass
class ClassDecl(Stmt):
    name: str = ""
    superclass: Optional[str] = None
    methods: List[FunctionDecl] = field(default_factory=list)
    static_methods: List[FunctionDecl] = field(default_factory=list)


@dataclass
class IfStmt(Stmt):
    condition: Expr = field(default_factory=Expr)
    then_branch: Stmt = field(default_factory=Stmt)
    else_branch: Optional[Stmt] = None


@dataclass
class WhileStmt(Stmt):
    condition: Expr = field(default_factory=Expr)
    body: Stmt = field(default_factory=Stmt)


@dataclass
class RepeatStmt(Stmt):
    count: Expr = field(default_factory=Expr)
    body: Stmt = field(default_factory=Stmt)


@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr] = None


@dataclass
class BreakStmt(Stmt):
    pass


@dataclass
class ContinueStmt(Stmt):
    pass


@dataclass
class ImportStmt(Stmt):
    module_name: str = ""
    alias: Optional[str] = None
    symbols: Optional[List[str]] = None


@dataclass
class Program(ASTNode):
    statements: List[Stmt] = field(default_factory=list)
    has_boundaries: bool = False


# ============================================================================
# Visitor Base
# ============================================================================

class ASTVisitor:
    """Base visitor interface for AST traversal."""

    def generic_visit(self, node: ASTNode) -> Any:
        raise NotImplementedError(
            f"No visit_{node.__class__.__name__} method defined on {self.__class__.__name__}"
        )

