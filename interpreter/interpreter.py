"""HAKAI Tree-Walk AST Interpreter."""

from __future__ import annotations

import os
from typing import Any, List, Optional
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
    Set,
    Index,
    IndexSet,
    ArrayLiteral,
    MapLiteral,
    TupleLiteral,
)
from compiler.errors import (
    HakaiBreakSignal,
    HakaiContinueSignal,
    HakaiError,
    HakaiIndexError,
    HakaiKeyError,
    HakaiNameError,
    HakaiReturnSignal,
    HakaiRuntimeError,
    HakaiTypeError,
)
from interpreter.environment import Environment
from interpreter.values import (
    HakaiCallable,
    hakai_to_str,
    hakai_type_name,
    is_truthy,
)
from interpreter.functions import HakaiFunction
from interpreter.classes import HakaiClass, HakaiInstance
from interpreter.runtime import RuntimeContext


class Interpreter(ASTVisitor):
    """Executes HAKAI AST programs via tree walking."""

    def __init__(
        self,
        runtime_context: Optional[RuntimeContext] = None,
        base_dir: str = ".",
    ) -> None:
        self.runtime_context = runtime_context or RuntimeContext()
        self.base_dir = base_dir
        self.globals = Environment()
        self.environment = self.globals

        # Inject global builtins
        for name, fn in self.runtime_context.get_builtins().items():
            self.globals.define(name, fn)

    def interpret(self, program: Program) -> Any:
        try:
            return self.visit_Program(program)
        except HakaiError:
            raise
        except Exception as exc:
            raise HakaiRuntimeError(f"Unexpected internal runtime error: {exc}")

    def evaluate(self, expr: ASTNode, env: Optional[Environment] = None) -> Any:
        if env is not None:
            prev = self.environment
            self.environment = env
            try:
                return expr.accept(self)
            finally:
                self.environment = prev
        return expr.accept(self)

    def execute_block(self, statements: List[ASTNode], env: Environment) -> None:
        previous = self.environment
        try:
            self.environment = env
            for stmt in statements:
                stmt.accept(self)
        finally:
            self.environment = previous

    # =========================================================================
    # Statement Visitors
    # =========================================================================

    def visit_Program(self, node: Program) -> Any:
        result = None
        for statement in node.statements:
            result = statement.accept(self)
        return result

    def visit_Block(self, node: Block) -> None:
        self.execute_block(node.statements, Environment(enclosing=self.environment))

    def visit_VarDecl(self, node: VarDecl) -> None:
        value = None
        if node.initializer is not None:
            value = self.evaluate(node.initializer)
        self.environment.define(node.name, value, is_const=node.is_const)

    def visit_FunctionDecl(self, node: FunctionDecl) -> None:
        function = HakaiFunction(node, self.environment, is_initializer=False)
        self.environment.define(node.name, function)

    def visit_ClassDecl(self, node: ClassDecl) -> None:
        superclass: Optional[HakaiClass] = None
        if node.superclass is not None:
            sc_val = self.environment.get(
                node.superclass, node.filename, node.line, node.column
            )
            if not isinstance(sc_val, HakaiClass):
                raise HakaiTypeError(
                    f"Superclass '{node.superclass}' must be a class, got {hakai_type_name(sc_val)}.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            superclass = sc_val

        methods = {}
        for m_decl in node.methods:
            is_init = m_decl.name == "init"
            m = HakaiFunction(m_decl, self.environment, is_initializer=is_init)
            methods[m_decl.name] = m

        static_methods = {}
        for sm_decl in node.static_methods:
            sm = HakaiFunction(sm_decl, self.environment, is_initializer=False)
            static_methods[sm_decl.name] = sm

        klass = HakaiClass(
            name=node.name,
            superclass=superclass,
            methods=methods,
            static_methods=static_methods,
        )
        self.environment.define(node.name, klass)

    def visit_IfStmt(self, node: IfStmt) -> None:
        cond_val = self.evaluate(node.condition)
        if is_truthy(cond_val):
            node.then_branch.accept(self)
        elif node.else_branch is not None:
            node.else_branch.accept(self)

    def visit_WhileStmt(self, node: WhileStmt) -> None:
        while is_truthy(self.evaluate(node.condition)):
            try:
                node.body.accept(self)
            except HakaiBreakSignal:
                break
            except HakaiContinueSignal:
                continue

    def visit_RepeatStmt(self, node: RepeatStmt) -> None:
        count_val = self.evaluate(node.count)
        if not isinstance(count_val, int) or count_val < 0:
            raise HakaiTypeError(
                f"Repeat loop count must be a non-negative integer, got {hakai_type_name(count_val)} ({count_val}).",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )
        for _ in range(count_val):
            try:
                node.body.accept(self)
            except HakaiBreakSignal:
                break
            except HakaiContinueSignal:
                continue

    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        value = None
        if node.value is not None:
            value = self.evaluate(node.value)
        raise HakaiReturnSignal(value)

    def visit_BreakStmt(self, node: BreakStmt) -> None:
        raise HakaiBreakSignal()

    def visit_ContinueStmt(self, node: ContinueStmt) -> None:
        raise HakaiContinueSignal()

    def visit_ImportStmt(self, node: ImportStmt) -> None:
        mod_dict = self.runtime_context.load_module(
            node.module_name, current_dir=self.base_dir
        )
        if node.symbols is not None:
            for sym in node.symbols:
                if sym not in mod_dict:
                    raise HakaiNameError(
                        f"Module '{node.module_name}' does not export symbol '{sym}'.",
                        filename=node.filename,
                        line=node.line,
                        column=node.column,
                    )
                self.environment.define(sym, mod_dict[sym])
        else:
            # Whole module object
            mod_obj = HakaiModuleObject(node.module_name, mod_dict)
            target_name = node.alias or node.module_name
            self.environment.define(target_name, mod_obj)

    def visit_ExpressionStmt(self, node: ExpressionStmt) -> Any:
        return self.evaluate(node.expression)

    # =========================================================================
    # Expression Visitors
    # =========================================================================

    def visit_Literal(self, node: Literal) -> Any:
        return node.value

    def visit_Identifier(self, node: Identifier) -> Any:
        return self.environment.get(
            node.name, filename=node.filename, line=node.line, column=node.column
        )

    def visit_SelfNode(self, node: SelfNode) -> Any:
        return self.environment.get(
            "self", filename=node.filename, line=node.line, column=node.column
        )

    def visit_SuperNode(self, node: SuperNode) -> Any:
        self_obj = self.environment.get(
            "self", filename=node.filename, line=node.line, column=node.column
        )
        if not isinstance(self_obj, HakaiInstance):
            raise HakaiTypeError(
                "'super' used outside of class instance method.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )
        sc = self_obj.klass.superclass
        if sc is None:
            raise HakaiTypeError(
                f"Class '{self_obj.klass.name}' has no superclass.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )
        method = sc.find_method(node.method)
        if method is None:
            raise HakaiNameError(
                f"Superclass '{sc.name}' has no method '{node.method}'.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )
        return method.bind(self_obj)

    def visit_Assign(self, node: Assign) -> Any:
        value = self.evaluate(node.value)
        self.environment.assign(
            node.name,
            value,
            filename=node.filename,
            line=node.line,
            column=node.column,
        )
        return value

    def visit_Binary(self, node: Binary) -> Any:
        # Short-circuit logical operators
        if node.operator in ("or", "||"):
            left_val = self.evaluate(node.left)
            if is_truthy(left_val):
                return left_val
            return self.evaluate(node.right)

        if node.operator in ("and", "&&"):
            left_val = self.evaluate(node.left)
            if not is_truthy(left_val):
                return left_val
            return self.evaluate(node.right)

        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        op = node.operator

        # String concatenation
        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return hakai_to_str(left) + hakai_to_str(right)
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            raise HakaiTypeError(
                f"Operator '+' not supported between {hakai_type_name(left)} and {hakai_type_name(right)}.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

        if op == "-":
            self._check_numbers(left, right, op, node)
            return left - right

        if op == "*":
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            if isinstance(left, list) and isinstance(right, int):
                return left * right
            self._check_numbers(left, right, op, node)
            return left * right

        if op == "/":
            self._check_numbers(left, right, op, node)
            if right == 0:
                raise HakaiRuntimeError(
                    "Division by zero.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            return left / right

        if op == "%":
            self._check_numbers(left, right, op, node)
            if right == 0:
                raise HakaiRuntimeError(
                    "Modulo by zero.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            return left % right

        if op == "**":
            self._check_numbers(left, right, op, node)
            return left**right

        # Comparison
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            self._check_comparable(left, right, op, node)
            return left < right
        if op == "<=":
            self._check_comparable(left, right, op, node)
            return left <= right
        if op == ">":
            self._check_comparable(left, right, op, node)
            return left > right
        if op == ">=":
            self._check_comparable(left, right, op, node)
            return left >= right

        raise HakaiRuntimeError(
            f"Unknown operator: {op}",
            filename=node.filename,
            line=node.line,
            column=node.column,
        )

    def visit_Unary(self, node: Unary) -> Any:
        operand = self.evaluate(node.operand)
        op = node.operator

        if op in ("not", "!"):
            return not is_truthy(operand)
        if op == "-":
            if not isinstance(operand, (int, float)):
                raise HakaiTypeError(
                    f"Unary '-' expects a number, got {hakai_type_name(operand)}.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            return -operand
        if op == "+":
            if not isinstance(operand, (int, float)):
                raise HakaiTypeError(
                    f"Unary '+' expects a number, got {hakai_type_name(operand)}.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            return operand

        raise HakaiRuntimeError(
            f"Unknown unary operator: {op}",
            filename=node.filename,
            line=node.line,
            column=node.column,
        )

    def visit_Call(self, node: Call) -> Any:
        callee = self.evaluate(node.callee)
        arguments = [self.evaluate(arg) for arg in node.arguments]

        if not isinstance(callee, HakaiCallable):
            raise HakaiTypeError(
                f"Object of type '{hakai_type_name(callee)}' is not callable.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

        return callee.call(
            self,
            arguments,
            filename=node.filename,
            line=node.line,
            column=node.column,
        )

    def visit_Get(self, node: Get) -> Any:
        obj = self.evaluate(node.obj)

        if isinstance(obj, HakaiInstance):
            return obj.get(
                node.name, filename=node.filename, line=node.line, column=node.column
            )
        if isinstance(obj, HakaiClass):
            return obj.get_static(
                node.name, filename=node.filename, line=node.line, column=node.column
            )
        if isinstance(obj, HakaiModuleObject):
            return obj.get(
                node.name, filename=node.filename, line=node.line, column=node.column
            )
        if hasattr(obj, "get_method"):
            return obj.get_method(node.name)
        if isinstance(obj, dict) and node.name in obj:
            return obj[node.name]

        raise HakaiTypeError(
            f"Cannot access property '{node.name}' on {hakai_type_name(obj)}.",
            filename=node.filename,
            line=node.line,
            column=node.column,
        )

    def visit_Set(self, node: Set) -> Any:
        obj = self.evaluate(node.obj)
        val = self.evaluate(node.value)

        if isinstance(obj, HakaiInstance):
            obj.set(node.name, val)
            return val
        if isinstance(obj, dict):
            obj[node.name] = val
            return val

        raise HakaiTypeError(
            f"Cannot set property '{node.name}' on {hakai_type_name(obj)}.",
            filename=node.filename,
            line=node.line,
            column=node.column,
        )

    def visit_Index(self, node: Index) -> Any:
        target = self.evaluate(node.target)
        idx = self.evaluate(node.index)

        if isinstance(target, (list, tuple, str)):
            if not isinstance(idx, int):
                raise HakaiTypeError(
                    f"Index must be an integer, got {hakai_type_name(idx)}.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            if idx < -len(target) or idx >= len(target):
                raise HakaiIndexError(
                    f"Index out of range: {idx} (size {len(target)}).",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            return target[idx]

        if isinstance(target, dict):
            if idx not in target:
                raise HakaiKeyError(
                    f"Key not found in map: {idx!r}.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            return target[idx]

        raise HakaiTypeError(
            f"Subscript indexing not supported on {hakai_type_name(target)}.",
            filename=node.filename,
            line=node.line,
            column=node.column,
        )

    def visit_IndexSet(self, node: IndexSet) -> Any:
        target = self.evaluate(node.target)
        idx = self.evaluate(node.index)
        val = self.evaluate(node.value)

        if isinstance(target, list):
            if not isinstance(idx, int):
                raise HakaiTypeError(
                    f"Index must be an integer, got {hakai_type_name(idx)}.",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            if idx < -len(target) or idx >= len(target):
                raise HakaiIndexError(
                    f"Index out of range: {idx} (size {len(target)}).",
                    filename=node.filename,
                    line=node.line,
                    column=node.column,
                )
            target[idx] = val
            return val

        if isinstance(target, dict):
            target[idx] = val
            return val

        raise HakaiTypeError(
            f"Cannot assign to index on {hakai_type_name(target)}.",
            filename=node.filename,
            line=node.line,
            column=node.column,
        )

    def visit_ArrayLiteral(self, node: ArrayLiteral) -> List[Any]:
        return [self.evaluate(elem) for elem in node.elements]

    def visit_MapLiteral(self, node: MapLiteral) -> dict:
        m = {}
        for k_expr, v_expr in node.pairs:
            k = self.evaluate(k_expr)
            v = self.evaluate(v_expr)
            m[k] = v
        return m

    def visit_TupleLiteral(self, node: TupleLiteral) -> tuple:
        return tuple(self.evaluate(elem) for elem in node.elements)

    # -------------------------------------------------------------------------
    # Validation helpers
    # -------------------------------------------------------------------------

    def _check_numbers(self, a: Any, b: Any, op: str, node: ASTNode) -> None:
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
            raise HakaiTypeError(
                f"Operator '{op}' requires numeric operands, got {hakai_type_name(a)} and {hakai_type_name(b)}.",
                filename=node.filename,
                line=node.line,
                column=node.column,
            )

    def _check_comparable(self, a: Any, b: Any, op: str, node: ASTNode) -> None:
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return
        if isinstance(a, str) and isinstance(b, str):
            return
        raise HakaiTypeError(
            f"Cannot compare {hakai_type_name(a)} with {hakai_type_name(b)} using '{op}'.",
            filename=node.filename,
            line=node.line,
            column=node.column,
        )


class HakaiModuleObject:
    """Wrapper representing an imported module namespace."""

    def __init__(self, name: str, symbols: dict) -> None:
        self.name = name
        self.symbols = symbols

    def get(
        self,
        name: str,
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        if name in self.symbols:
            return self.symbols[name]
        raise HakaiNameError(
            f"Module '{self.name}' has no attribute '{name}'.",
            filename=filename,
            line=line,
            column=column,
            source_code=source_code,
        )

    def __hakai_str__(self) -> str:
        return f"<module '{self.name}'>"

    def __repr__(self) -> str:
        return self.__hakai_str__()

