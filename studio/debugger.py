"""Execution and Debugging engine controller for HAKAI Studio."""

from __future__ import annotations

import io
from typing import Optional
from compiler.compiler import Compiler
from compiler.lexer import Lexer
from compiler.parser import Parser
from interpreter.interpreter import Interpreter
from interpreter.runtime import RuntimeContext
from virtual_machine.vm import VirtualMachine


class ExecutionController:
    """Executes HAKAI scripts and bytecode with redirected output capture."""

    @staticmethod
    def run_source(source: str, filename: str = "<editor>") -> tuple[str, Optional[str]]:
        """Run source through HAKAI interpreter. Returns (stdout, error_message)."""
        buf = io.StringIO()
        ctx = RuntimeContext(stdout=buf)
        try:
            tokens = Lexer(source=source, filename=filename).tokenize()
            ast = Parser(tokens=tokens, source_code=source).parse()
            interp = Interpreter(runtime_context=ctx)
            interp.interpret(ast)
            return buf.getvalue(), None
        except Exception as err:
            return buf.getvalue(), str(err)

    @staticmethod
    def compile_source(source: str, filename: str = "<editor>") -> tuple[Optional[bytes], Optional[str]]:
        """Compile source into bytecode. Returns (serialized_bytecode, error_message)."""
        try:
            compiler = Compiler()
            code_obj = compiler.compile(source, filename=filename)
            return code_obj.serialize(), None
        except Exception as err:
            return None, str(err)

    @staticmethod
    def run_bytecode(bytecode_data: bytes) -> tuple[str, Optional[str]]:
        """Run bytecode in HAKAI Virtual Machine. Returns (stdout, error_message)."""
        from virtual_machine.instructions import HakaiCodeObject
        buf = io.StringIO()
        try:
            code_obj = HakaiCodeObject.deserialize(bytecode_data)
            vm = VirtualMachine(stdout=buf)
            vm.run(code_obj)
            return buf.getvalue(), None
        except Exception as err:
            return buf.getvalue(), str(err)

