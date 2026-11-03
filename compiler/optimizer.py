"""AST and Bytecode Optimizer for HAKAI Compiler."""

from __future__ import annotations

from typing import Any, List
from compiler.ast_nodes import (
    ASTNode,
    Binary,
    Block,
    BreakStmt,
    ContinueStmt,
    ExpressionStmt,
    IfStmt,
    Literal,
    Program,
    ReturnStmt,
    Stmt,
    Unary,
    VarDecl,
    WhileStmt,
    RepeatStmt,
)


class ASTOptimizer:
    """Performs constant folding and dead code elimination on the AST."""

    def optimize(self, program: Program) -> Program:
        new_stmts = self._optimize_statements(program.statements)
        program.statements = new_stmts
        return program

    def _optimize_statements(self, statements: List[Stmt]) -> List[Stmt]:
        optimized: List[Stmt] = []
        for stmt in statements:
            opt_stmt = self._optimize_node(stmt)
            if opt_stmt is not None:
                optimized.append(opt_stmt)
                # Dead code elimination: ignore statements after return, break, or continue in same block
                if isinstance(opt_stmt, (ReturnStmt, BreakStmt, ContinueStmt)):
                    break
        return optimized

    def _optimize_node(self, node: ASTNode) -> Any:
        if isinstance(node, Block):
            node.statements = self._optimize_statements(node.statements)
            return node

        if isinstance(node, VarDecl) and node.initializer is not None:
            node.initializer = self._fold_expression(node.initializer)
            return node

        if isinstance(node, ExpressionStmt):
            node.expression = self._fold_expression(node.expression)
            return node

        if isinstance(node, IfStmt):
            node.condition = self._fold_expression(node.condition)
            node.then_branch = self._optimize_node(node.then_branch)
            if node.else_branch is not None:
                node.else_branch = self._optimize_node(node.else_branch)
            return node

        if isinstance(node, WhileStmt):
            node.condition = self._fold_expression(node.condition)
            node.body = self._optimize_node(node.body)
            return node

        if isinstance(node, RepeatStmt):
            node.count = self._fold_expression(node.count)
            node.body = self._optimize_node(node.body)
            return node

        return node

    def _fold_expression(self, expr: Any) -> Any:
        if isinstance(expr, Binary):
            left = self._fold_expression(expr.left)
            right = self._fold_expression(expr.right)
            expr.left = left
            expr.right = right

            # If both sides are literals, fold!
            if isinstance(left, Literal) and isinstance(right, Literal):
                val_l = left.value
                val_r = right.value
                op = expr.operator
                try:
                    if op == "+" and type(val_l) == type(val_r) and isinstance(val_l, (int, float, str)):
                        return Literal(value=val_l + val_r, line=expr.line, column=expr.column, filename=expr.filename)
                    elif op == "-" and isinstance(val_l, (int, float)) and isinstance(val_r, (int, float)):
                        return Literal(value=val_l - val_r, line=expr.line, column=expr.column, filename=expr.filename)
                    elif op == "*" and isinstance(val_l, (int, float)) and isinstance(val_r, (int, float)):
                        return Literal(value=val_l * val_r, line=expr.line, column=expr.column, filename=expr.filename)
                    elif op == "/" and isinstance(val_l, (int, float)) and isinstance(val_r, (int, float)) and val_r != 0:
                        return Literal(value=val_l / val_r, line=expr.line, column=expr.column, filename=expr.filename)
                except Exception:
                    pass
            return expr

        if isinstance(expr, Unary):
            operand = self._fold_expression(expr.operand)
            expr.operand = operand
            if isinstance(operand, Literal):
                val = operand.value
                op = expr.operator
                if op == "-" and isinstance(val, (int, float)):
                    return Literal(value=-val, line=expr.line, column=expr.column, filename=expr.filename)
            return expr

        return expr
