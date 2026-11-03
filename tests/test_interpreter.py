"""Comprehensive tests for the HAKAI Interpreter and Runtime."""

import io
import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from interpreter.interpreter import Interpreter
from interpreter.runtime import RuntimeContext
from compiler.errors import HakaiTypeError, HakaiNameError


def run_code(source: str) -> str:
    buf = io.StringIO()
    ctx = RuntimeContext(stdout=buf)
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source_code=source).parse()
    interp = Interpreter(runtime_context=ctx)
    interp.interpret(program)
    return buf.getvalue().strip()


def test_initial_acceptance_program():
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
    output = run_code(source)
    expected = "\n".join([
        "Welcome to HAKAI",
        "30",
        "HAKAI is working!"
    ])
    assert output == expected


def test_constants_immutability():
    source = """
    const PI = 3.14
    PI = 3.14159
    """
    with pytest.raises(HakaiTypeError) as exc:
        run_code(source)
    assert "Cannot reassign to constant" in str(exc.value)


def test_functions_and_recursion():
    source = """
    function factorial(n) {
        if n <= 1 {
            return 1
        }
        return n * factorial(n - 1)
    }

    print(factorial(5))
    """
    assert run_code(source) == "120"


def test_closures():
    source = """
    function make_multiplier(factor) {
        function mult(x) {
            return x * factor
        }
        return mult
    }

    let double = make_multiplier(2)
    let triple = make_multiplier(3)
    print(double(10))
    print(triple(10))
    """
    assert run_code(source) == "20\n30"


def test_loops_break_continue():
    source = """
    let sum = 0
    let i = 0
    while i < 10 {
        i = i + 1
        if i == 5 {
            continue
        }
        if i == 8 {
            break
        }
        sum = sum + i
    }
    print(sum)
    """
    # 1 + 2 + 3 + 4 + 6 + 7 = 23
    assert run_code(source) == "23"


def test_repeat_loop():
    source = """
    let count = 0
    repeat 4 {
        count = count + 10
    }
    print(count)
    """
    assert run_code(source) == "40"


def test_oop_inheritance_and_dispatch():
    source = """
    class Animal {
        function init(name) {
            self.name = name
        }

        function speak() {
            return self.name + " makes a sound."
        }
    }

    class Dog extends Animal {
        function speak() {
            return self.name + " barks!"
        }
    }

    let a = Animal("Creature")
    let d = Dog("Buddy")

    print(a.speak())
    print(d.speak())
    """
    expected = "Creature makes a sound.\nBuddy barks!"
    assert run_code(source) == expected


def test_arrays_and_maps():
    source = """
    let numbers = [10, 20, 30]
    numbers[1] = 99
    print(numbers[0])
    print(numbers[1])
    print(len(numbers))

    let user = {"name": "Alex", "age": 25}
    user["age"] = 26
    print(user["name"])
    print(user["age"])
    """
    expected = "10\n99\n3\nAlex\n26"
    assert run_code(source) == expected


def test_standard_math_and_strings():
    source = """
    import math
    import strings

    print(math.sqrt(144))
    print(math.pow(2, 3))
    print(strings.upper("hakai"))
    print(strings.contains("hello world", "world"))
    """
    expected = "12.0\n8.0\nHAKAI\ntrue"
    assert run_code(source) == expected

