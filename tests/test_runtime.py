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


def test_stdlib_path_resolution():
    from stdlib import get_stdlib_path
    stdlib_dir = get_stdlib_path()
    assert stdlib_dir is not None
    assert os.path.isdir(stdlib_dir)
    assert os.path.isfile(os.path.join(stdlib_dir, "math.hakai"))


def test_stdlib_hakai_module_loading():
    import io
    buf = io.StringIO()
    ctx = RuntimeContext(stdout=buf)
    source = """
    import math
    // Test native builtin
    print(math.sqrt(64))
    // Test HAKAI stdlib function from stdlib/math.hakai
    print(math.clamp(150, 0, 100))
    print(math.is_even(42))
    """
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    Interpreter(runtime_context=ctx).interpret(program)
    lines = buf.getvalue().strip().splitlines()
    assert lines == ["8.0", "100", "true"]


def test_circular_import_detection():
    import pytest
    from compiler.errors import HakaiImportError
    with tempfile.TemporaryDirectory() as tmpdir:
        mod_a = os.path.join(tmpdir, "mod_a.hakai")
        mod_b = os.path.join(tmpdir, "mod_b.hakai")
        with open(mod_a, "w", encoding="utf-8") as f:
            f.write('import mod_b\n')
        with open(mod_b, "w", encoding="utf-8") as f:
            f.write('import mod_a\n')

        ctx = RuntimeContext()
        with pytest.raises(HakaiImportError) as exc_info:
            ctx.load_module("mod_a", current_dir=tmpdir)
        assert "Circular import detected" in str(exc_info.value)

