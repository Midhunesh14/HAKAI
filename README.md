# HAKAI Programming Language (v1.0.0)

[![Tests](https://img.shields.io/badge/tests-37%2F37%20passing-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**HAKAI** is an independent, general-purpose programming language built from scratch. It provides clean syntax, strict lexical scoping, first-class functions and OOP, both an AST-based tree-walk interpreter and an optimizing bytecode compiler paired with a stack-based virtual machine (`HVM`), a desktop IDE (**HAKAI Studio**), and a dedicated package manager (**HPM**).

---

## Key Features

1. **Original Syntax & Grammar**: Readable and structured syntax with optional program demarcations (`HAKAI START` ... `HAKAI END`), brace blocks `{ ... }`, and clear control structures (`repeat N`, `while`, `if`, `else if`, `else`).
2. **Dual Execution Pipeline**:
   - **AST Interpreter**: Fast, interactive feedback and scripting with scope environments.
   - **Bytecode Compiler & Virtual Machine (HVM)**: Constant-folding optimizer, bytecode instruction generation, binary file emission (`.hbc`), and portable stack-based execution.
3. **First-Class Functions & OOP**:
   - Closures and lexical environment capture.
   - Default parameter values and recursive execution.
   - Class definitions with constructors (`init`), instance methods, single inheritance (`extends`), and static methods.
4. **Rich Type System**:
   - Primitives: `Integer`, `Float`, `String`, `Boolean`, `Null`.
   - Collections: dynamic `Array`, key-value `Map`, immutable `Tuple`.
   - Safe operations with explicit type conversion functions (`str()`, `int()`, `float()`, `bool()`, `len()`, `type()`).
5. **Standard Library**: Built-in and standard modules for `math`, `strings`, `collections`, `files`, `io`, and `system`.
6. **HAKAI Studio IDE**: PySide6 desktop IDE with custom dark styling, syntax highlighting, line numbers gutter, auto-indentation, project file tree, and live execution panel.
7. **HPM (HAKAI Package Manager)**: Manifest-based (`hakai.toml`) package management, dependency resolution, lockfile creation (`hakai.lock`), and local caching.

---

## Quick Start

### 1. Installation
Clone or open the repository in Python 3.10+:
```bash
pip install -r requirements.txt
```
To run the automated test suite:
```bash
python -m pytest tests/ -v
```

### 2. Running a HAKAI Script
Create a file named `hello.hakai`:
```hakai
HAKAI START

let greeting = "Hello from HAKAI!"
print(greeting)

HAKAI END
```
Execute using the interpreter:
```bash
python main.py run hello.hakai
```

### 3. Compiling to Bytecode & Running on the VM
Compile the source file into `.hbc` bytecode:
```bash
python main.py build hello.hakai
```
Execute the compiled bytecode with the HAKAI Virtual Machine:
```bash
python main.py run hello.hbc
```

### 4. Interactive REPL
```bash
python main.py repl
```
```
>>> let x = 10
>>> let y = 20
>>> print(x + y)
30
```

### 5. Launch HAKAI Studio Desktop IDE
```bash
python main.py studio
```

---

## Language Syntax at a Glance

### Variables and Constants
```hakai
let message = "Welcome"
let count = 0
count = count + 1

const PI = 3.14159265
// PI = 3.14  <-- Raises HakaiTypeError: Cannot reassign to constant
```

### Functions and Closures
```hakai
function make_adder(amount) {
    function adder(x) {
        return x + amount
    }
    return adder
}

let add10 = make_adder(10)
print(add10(5)) // 15
```

### Object-Oriented Programming
```hakai
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

let buddy = Dog("Buddy")
print(buddy.speak()) // Buddy barks!
```

### Loops
```hakai
// Fixed repetition loop
repeat 3 {
    print("HAKAI")
}

// While loop with break/continue
let i = 0
while i < 10 {
    i = i + 1
    if i == 5 {
        continue
    }
    print(i)
}
```

### Standard Library Imports
```hakai
import math
import strings

print(math.sqrt(144)) // 12.0
print(strings.upper("hakai")) // HAKAI
```

---

## HPM Package Manager

Initialize a new project:
```bash
python -m package_manager.cli init my_project
```
Manifest (`hakai.toml`):
```toml
[package]
name = "my_project"
version = "1.0.0"
entry = "main.hakai"

[dependencies]
math_extra = "0.1.0"
```
Install dependencies:
```bash
python -m package_manager.cli install
```

---

## Documentation

Full language and toolchain documentation is available in [`docs/`](docs/):
- [Language Specification](docs/LANGUAGE_SPECIFICATION.md)
- [Syntax Reference](docs/SYNTAX.md)
- [Getting Started Guide](docs/GETTING_STARTED.md)
- [Functions Guide](docs/FUNCTIONS.md)
- [Object-Oriented Programming](docs/OOP.md)
- [Module System](docs/MODULES.md)
- [Compiler & VM Architecture](docs/COMPILER.md)
- [Standard Library Reference](docs/STANDARD_LIBRARY.md)
- [HPM Package Manager](docs/PACKAGE_MANAGER.md)
- [FAQ](docs/FAQ.md)

---

## License
HAKAI is released under the [MIT License](LICENSE).

