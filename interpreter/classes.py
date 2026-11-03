"""Object-Oriented Programming (Classes & Instances) for HAKAI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from compiler.errors import HakaiNameError, HakaiTypeError
from interpreter.values import HakaiCallable, hakai_to_str


class HakaiClass(HakaiCallable):
    """Runtime representation of a HAKAI class."""

    def __init__(
        self,
        name: str,
        superclass: Optional[HakaiClass],
        methods: Dict[str, Any],
        static_methods: Dict[str, Any],
    ) -> None:
        self.name = name
        self.superclass = superclass
        self.methods = methods
        self.static_methods = static_methods

    @property
    def type_name(self) -> str:
        return "Class"

    def find_method(self, name: str) -> Optional[Any]:
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

    def find_static_method(self, name: str) -> Optional[Any]:
        if name in self.static_methods:
            return self.static_methods[name]
        if self.superclass is not None:
            return self.superclass.find_static_method(name)
        return None

    def arity(self) -> Tuple[int, int]:
        init = self.find_method("init")
        if init is not None:
            return init.arity()
        return (0, 0)

    def call(
        self,
        interpreter: Any,
        arguments: List[Any],
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        instance = HakaiInstance(self)
        init_method = self.find_method("init")
        if init_method is not None:
            bound_init = init_method.bind(instance)
            bound_init.call(
                interpreter=interpreter,
                arguments=arguments,
                filename=filename,
                line=line,
                column=column,
                source_code=source_code,
            )
        elif len(arguments) > 0:
            raise HakaiTypeError(
                message=f"Class '{self.name}' takes 0 constructor arguments, but {len(arguments)} were given.",
                filename=filename,
                line=line,
                column=column,
                source_code=source_code,
            )
        return instance

    def get_static(
        self,
        name: str,
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        static_m = self.find_static_method(name)
        if static_m is not None:
            return static_m
        raise HakaiNameError(
            message=f"No static method '{name}' found on class '{self.name}'.",
            filename=filename,
            line=line,
            column=column,
            source_code=source_code,
        )

    def __hakai_str__(self) -> str:
        return f"<class {self.name}>"

    def __repr__(self) -> str:
        return self.__hakai_str__()


class HakaiInstance:
    """Runtime instance of a HAKAI class."""

    def __init__(self, klass: HakaiClass) -> None:
        self.klass = klass
        self.fields: Dict[str, Any] = {}

    @property
    def type_name(self) -> str:
        return self.klass.name

    def get(
        self,
        name: str,
        filename: str = "<source>",
        line: int = 1,
        column: int = 1,
        source_code: Optional[str] = None,
    ) -> Any:
        if name in self.fields:
            return self.fields[name]

        method = self.klass.find_method(name)
        if method is not None:
            return method.bind(self)

        raise HakaiNameError(
            message=f"Undefined property or method '{name}' on {self.klass.name} instance.",
            filename=filename,
            line=line,
            column=column,
            source_code=source_code,
            suggestion=f"Make sure '{name}' is initialized in 'init' or declared as a method.",
        )

    def set(self, name: str, value: Any) -> None:
        self.fields[name] = value

    def __hakai_str__(self) -> str:
        # Check if user defined a toString() or describe() method
        for m_name in ("toString", "describe", "__str__"):
            m = self.klass.find_method(m_name)
            if m is not None:
                try:
                    res = m.bind(self).call(None, [])
                    if isinstance(res, str):
                        return res
                except Exception:
                    pass
        fields_str = ", ".join(f"{k}: {hakai_to_str(v)}" for k, v in self.fields.items())
        return f"<{self.klass.name} {{{fields_str}}}>"

    def __repr__(self) -> str:
        return self.__hakai_str__()

