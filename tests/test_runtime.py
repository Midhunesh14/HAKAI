"""Tests for runtime context, file handling, and stdlib."""

import os
import tempfile
from interpreter.interpreter import Interpreter
from interpreter.runtime import RuntimeContext
from compiler.lexer import Lexer
from compiler.parser import Parser


def test_file_io_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt").replace("\\", "/")
        source = f"""
        let f = open("{test_file}", "w")
        f.write("Hello from HAKAI Filesystem")
        f.close()

        let f2 = open("{test_file}", "r")
        let content = f2.read()
        f2.close()

        print(content)
        """
        import io
        buf = io.StringIO()
        ctx = RuntimeContext(stdout=buf)
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        Interpreter(runtime_context=ctx).interpret(program)

        assert buf.getvalue().strip() == "Hello from HAKAI Filesystem"

