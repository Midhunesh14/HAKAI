"""Tests for HAKAI Virtual Machine execution and matching interpreter semantics."""

import io
from compiler.compiler import Compiler
from compiler.lexer import Lexer
from compiler.parser import Parser
from interpreter.interpreter import Interpreter
from interpreter.runtime import RuntimeContext
from virtual_machine.vm import VirtualMachine


def run_interpreter(source: str) -> str:
    buf = io.StringIO()
    ctx = RuntimeContext(stdout=buf)
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source_code=source).parse()
    Interpreter(runtime_context=ctx).interpret(program)
    return buf.getvalue().strip()


def run_vm(source: str) -> str:
    buf = io.StringIO()
    compiler = Compiler()
    code_obj = compiler.compile(source)
    vm = VirtualMachine(stdout=buf)
    vm.run(code_obj)
    return buf.getvalue().strip()


def test_vm_acceptance_program():
    source = """
    HAKAI START

    let name = "HAKAI"

    print("Welcome to " + name)

    let a = 10
    let b = 20

    let total = a + b

    print(total)

    if total > 20 {
        print("HAKAI is working!")
    }
    else {
        print("Something went wrong!")
    }

    HAKAI END
    """
    interp_out = run_interpreter(source)
    vm_out = run_vm(source)
    assert vm_out == interp_out
    assert "HAKAI is working!" in vm_out


def test_vm_loops_and_conditionals():
    source = """
    let sum = 0
    let i = 0
    while i < 5 {
        i = i + 1
        sum = sum + i
    }
    print(sum)

    let count = 0
    repeat 3 {
        count = count + 5
    }
    print(count)
    """
    interp_out = run_interpreter(source)
    vm_out = run_vm(source)
    assert vm_out == interp_out
    assert vm_out == "15\n15"


def test_vm_collections():
    source = """
    let arr = [10, 20, 30]
    arr[1] = 99
    print(arr[0])
    print(arr[1])
    """
    interp_out = run_interpreter(source)
    vm_out = run_vm(source)
    assert vm_out == interp_out
    assert vm_out == "10\n99"
