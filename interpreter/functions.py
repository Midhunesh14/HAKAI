"""Function representation and execution for HAKAI."""

from __future__ import annotations

from typing import Any, List, Optional, Tuple
from compiler.ast_nodes import FunctionDecl
from compiler.errors import HakaiTypeError, HakaiReturnSignal
from interpreter.values import HakaiCallable
from interpreter.environment import Environment


class HakaiFunction(HakaiCallable):
    """User-defined HAKAI function with closure support."""

    def __init__(
        self,
        declaration: FunctionDecl,
        closure: Environment,
        is_initializer: bool = False,
    ) -> None:
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    @property
    def name(self) -> str:
        return self.declaration.name

    def arity(self) -> Tuple[int, int]:
        total = len(self.declaration.params)
        required = sum(1 for p in self.declaration.params if p.default_value is None)
        return (required, total)

    def bind(self, instance: Any) -> HakaiFunction:
        """Bind 'self' to an instance and return a bound method."""
        env = Environment(enclosing=self.closure)
        env.define("self", instance)
        return HakaiFunction(
            declaration=self.declaration,
            closure=env,
            is_initializer=self.is_initializer,
        )

    def call(
        self,
        interpreter: Any,
        arguments: List[Any],
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        params = self.declaration.params
        req_count, max_count = self.arity()

        if len(arguments) < req_count or len(arguments) > max_count:
            raise HakaiTypeError(
                message=f"Function '{self.name}' expects {req_count} to {max_count} arguments, got {len(arguments)}.",
                filename=filename,
                line=line,
                column=column,
                source_code=source_code,
            )

        call_env = Environment(enclosing=self.closure)

        for i, param in enumerate(params):
            if i < len(arguments):
                call_env.define(param.name, arguments[i])
            else:
                # Default parameter value
                val = interpreter.evaluate(param.default_value, call_env) if param.default_value else None
                call_env.define(param.name, val)

        try:
            interpreter.execute_block(self.declaration.body.statements, call_env)
        except HakaiReturnSignal as ret:
            if self.is_initializer:
                return self.closure.get("self", filename, line, column, source_code)
            return ret.value

        if self.is_initializer:
            return self.closure.get("self", filename, line, column, source_code)
        return None

    def __hakai_str__(self) -> str:
        return f"<function {self.name}>"

    def __repr__(self) -> str:
        return self.__hakai_str__()
