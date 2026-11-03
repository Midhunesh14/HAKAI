"""End-to-end integration tests for HAKAI 1.0."""

import io
from compiler.compiler import Compiler
from compiler.lexer import Lexer
from compiler.parser import Parser
from interpreter.interpreter import Interpreter
from interpreter.runtime import RuntimeContext
from virtual_machine.vm import VirtualMachine


def test_section_17_acceptance_specification():
    source = """
    HAKAI START

    let a = 100
    let b = 200

    function multiply(x, y) {
        return x * y
    }

    let result = multiply(a, b)

    if result == 20000 {
        print("TEST PASSED")
    }
    else {
        print("TEST FAILED")
    }

    HAKAI END
    """

    # 1. Interpreter execution
    buf_interp = io.StringIO()
    ctx = RuntimeContext(stdout=buf_interp)
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source_code=source).parse()
    interp = Interpreter(runtime_context=ctx)
    interp.interpret(program)
    assert buf_interp.getvalue().strip() == "TEST PASSED"

    # 2. Bytecode Compiler & VM execution
    buf_vm = io.StringIO()
    compiler = Compiler()
    code_obj = compiler.compile(source)
    vm = VirtualMachine(stdout=buf_vm)
    vm.run(code_obj)
    assert buf_vm.getvalue().strip() == "TEST PASSED"


def test_cli_integration_runner(tmp_path):
    from cli.commands import main as cli_main
    script_path = str(tmp_path / "app.hakai")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write('HAKAI START\nprint("Integration Success")\nHAKAI END\n')

    # Test check command
    ret_check = cli_main(["check", script_path])
    assert ret_check == 0

    # Test build command
    ret_build = cli_main(["build", script_path])
    assert ret_build == 0
    hbc_path = str(tmp_path / "app.hbc")

    # Test run bytecode command
    ret_run_bc = cli_main(["run", hbc_path])
    assert ret_run_bc == 0

