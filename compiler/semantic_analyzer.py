"""Semantic Analyzer for the HAKAI Compiler."""

from __future__ import annotations

from typing import Dict, List, Optional, Set
from compiler.ast_nodes import (
    ASTNode,
    ASTVisitor,
    Program,
    Block,
    VarDecl,
    FunctionDecl,
    ClassDecl,
    IfStmt,
    WhileStmt,
    RepeatStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    ImportStmt,
    ExpressionStmt,
    Literal,
    Identifier,
    SelfNode,
    SuperNode,
    Assign,
    Binary,
    Unary,
    Call,
    Get,
    Set as AstSet,
    Index,
    IndexSet,
    ArrayLiteral,
    MapLiteral,
    TupleLiteral,
)
from compiler.errors import HakaiSemanticError


class Symbol:
    def __init__(self, name: str, is_const: bool = False) -> None:
        self.name = name
        self.is_const = is_const


class Scope:
    def __init__(self, enclosing: Optional[Scope] = None) -> None:
        self.enclosing = enclosing
        self.symbols: Dict[str, Symbol] = {}

    def define(self, name: str, is_const: bool = False) -> None:
        self.symbols[name] = Symbol(name, is_const)

    def is_defined_local(self, name: str) -> bool:
        return name in self.symbols

    def resolve(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.enclosing is not None:
            return self.enclosing.resolve(name)
        return None


class SemanticAnalyzer(ASTVisitor):
    """Performs static checks, symbol resolution, and scope validation."""

    def __init__(self) -> None:
        self.current_scope = Scope()
        self.loop_depth = 0
        self.function_depth = 0
        self.in_class = False

        # Predefine known builtins
        builtins = [
            "print", "println", "type", "len", "str", "int",
            "float", "bool", "range", "open", "input"
        ]
        for b in builtins:
            self.current_scope.define(b, is_const=True)

    def analyze(self, program: Program) -> None:
        self.visit_Program(program)

    def visit_Program(self, node: Program) -> None:
        for stmt in node.statements:
            stmt.accept(self)

    def visit_Block(self, node: Block) -> None:
        prev_scope = self.current_scope
        self.current_scope = Scope(enclosing=prev_scope)
        try:
            for stmt in node.statements:
                stmt.accept(self)
        finally:
            self.current_scope = prev_scope

    def visit_VarDecl(self, node: VarDecl) -> None:
        if node.initializer is not None:
            node.initializer.accept(self)
        self.current_scope.define(node.name, is_const=node.is_const)

    def visit_FunctionDecl(self, node: FunctionDecl) -> None:
        self.current_scope.define(node.name, is_const=False)

        prev_scope = self.current_scope
        self.current_scope = Scope(enclosing=prev_scope)
        self.function_depth += 1
        try:
            for param in node.params:
                if param.default_value is not None:
                    param.default_value.accept(self)
                self.current_scope.define(param.name, is_const=False)
            node.body.accept(self)
        finally:
            self.function_depth -= 1
            self.current_scope = prev_scope

    def visit_ClassDecl(self, node: ClassDecl) -> None:
        self.current_scope.define(node.name, is_const=True)
        prev_in_class = self.in_class
        self.in_class = True
        try:
            for m in node.methods:
                m.accept(self)
            for sm in node.static_methods:
                sm.accept(self)
        finally:
            self.in_class = prev_in_class

    def visit_IfStmt(self, node: IfStmt) -> None:
        node.condition.accept(self)
        node.then_branch.accept(self)
        if node.else_branch is not None:
            node.else_branch.accept(self)

    def visit_WhileStmt(self, node: WhileStmt) -> None:
        node.condition.accept(self)
        self.loop_depth += 1
        try:
            node.body.accept(self)
        finally:
            self.loop_depth -= 1

    def visit_RepeatStmt(self, node: RepeatStmt) -> None:
        node.count.accept(self)
        self.loop_depth += 1
        try:
            node.body.accept(self)
        finally:
            self.loop_depth -= 1

    def visit_BreakStmt(self, node: BreakStmt) -> None:
        if self.loop_depth == 0:
            raise HakaiSemanticError(
                "Cannot use 'break' outside of a loop.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

    def visit_ContinueStmt(self, node: ContinueStmt) -> None:
        if self.loop_depth == 0:
            raise HakaiSemanticError(
                "Cannot use 'continue' outside of a loop.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        if self.function_depth == 0:
            raise HakaiSemanticError(
                "Cannot use 'return' outside of a function.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )
        if node.value is not None:
            node.value.accept(self)

    def visit_ImportStmt(self, node: ImportStmt) -> None:
        if node.symbols is not None:
            for sym in node.symbols:
                self.current_scope.define(sym, is_const=True)
        else:
            target = node.alias or node.module_name
            self.current_scope.define(target, is_const=True)

    def visit_ExpressionStmt(self, node: ExpressionStmt) -> None:
        node.expression.accept(self)

    def visit_Literal(self, node: Literal) -> None:
        pass

    def visit_Identifier(self, node: Identifier) -> None:
        # Resolve identifier
        sym = self.current_scope.resolve(node.name)
        # Note: in dynamic scripting language, forward references to functions are allowed
        # but if we're in static analysis we can check or register usage.

    def visit_SelfNode(self, node: SelfNode) -> None:
        if not self.in_class:
            raise HakaiSemanticError(
                "'self' cannot be referenced outside of a class method.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

    def visit_SuperNode(self, node: SuperNode) -> None:
        if not self.in_class:
            raise HakaiSemanticError(
                "'super' cannot be referenced outside of a class.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

    def visit_Assign(self, node: Assign) -> None:
        node.value.accept(self)
        sym = self.current_scope.resolve(node.name)
        if sym is not None and sym.is_const:
            raise HakaiSemanticError(
                f"Cannot reassign to constant '{node.name}'.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

    def visit_Binary(self, node: Binary) -> None:
        node.left.accept(self)
        node.right.accept(self)

    def visit_Unary(self, node: Unary) -> None:
        node.operand.accept(self)

    def visit_Call(self, node: Call) -> None:
        node.callee.accept(self)
        for arg in node.arguments:
            arg.accept(self)

    def visit_Get(self, node: Get) -> None:
        node.obj.accept(self)

    def visit_Set(self, node: AstSet) -> None:
        node.obj.accept(self)
        node.value.accept(self)

    def visit_Index(self, node: Index) -> None:
        node.target.accept(self)
        node.index.accept(self)

    def visit_IndexSet(self, node: IndexSet) -> None:
        node.target.accept(self)
        node.index.accept(self)
        node.value.accept(self)

    def visit_ArrayLiteral(self, node: ArrayLiteral) -> None:
        for elem in node.elements:
            elem.accept(self)

    def visit_MapLiteral(self, node: MapLiteral) -> None:
        for k, v in node.pairs:
            k.accept(self)
            v.accept(self)

    def visit_TupleLiteral(self, node: TupleLiteral) -> None:
        for elem in node.elements:
            elem.accept(self)

