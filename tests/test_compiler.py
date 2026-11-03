"""Tests for HAKAI Compiler, Bytecode Serialization, and Optimization."""

import os
import tempfile
from compiler.compiler import Compiler
from virtual_machine.instructions import HakaiCodeObject, Opcode


def test_compile_basic_program():
    source = """
    let a = 10
    let b = 20
    let c = a + b
    print(c)
    """
    compiler = Compiler()
    code_obj = compiler.compile(source)
    assert isinstance(code_obj, HakaiCodeObject)
    assert "a" in code_obj.names
    assert "b" in code_obj.names
    assert "c" in code_obj.names
    opcodes = [ins.opcode for ins in code_obj.instructions]
    assert Opcode.STORE_NAME in opcodes
    assert Opcode.ADD in opcodes
    assert Opcode.HALT in opcodes


def test_constant_folding():
    source = "let x = 10 + 20 * 2"
    compiler = Compiler()
    code_obj = compiler.compile(source)
    # 10 + 20 * 2 should fold to 50
    assert 50 in code_obj.constants


def test_bytecode_file_serialization():
    source = 'print("HAKAI Bytecode Works")'
    compiler = Compiler()
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "test.hakai")
        with open(src_file, "w", encoding="utf-8") as f:
            f.write(source)

        out_file = compiler.compile_to_file(src_file)
        assert os.path.exists(out_file)
        assert out_file.endswith(".hbc")

        with open(out_file, "rb") as f:
            data = f.read()

        deserialized = HakaiCodeObject.deserialize(data)
        assert deserialized.name == src_file
        assert "HAKAI Bytecode Works" in deserialized.constants

