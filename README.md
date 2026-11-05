# HAKAI Programming Language (v1.0.0)

[![CI Build & Test](https://github.com/Midhunesh14/HAKAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Midhunesh14/HAKAI/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-40%2F40%20passing-brightgreen.svg)]()
[![PyPI](https://img.shields.io/badge/PyPI-hakai--lang%20v1.0.0-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/hakai-lang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

> **PyPI Package**: [https://pypi.org/project/hakai-lang/](https://pypi.org/project/hakai-lang/)  
> **Source Repository**: [https://github.com/Midhunesh14/HAKAI](https://github.com/Midhunesh14/HAKAI)  
> **Release Downloads**: [GitHub Releases](https://github.com/Midhunesh14/HAKAI/releases)

**HAKAI** is an independent, general-purpose programming language built from scratch. It features clean syntax, strict lexical scoping, first-class functions and OOP, both an AST-based tree-walk interpreter and an optimizing bytecode compiler paired with a stack-based virtual machine (`HVM`), a desktop IDE (**HAKAI Studio**), and a dedicated package manager (**HPM**).

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
6. **HAKAI Studio IDE**: Desktop IDE with custom dark styling, syntax highlighting, line numbers gutter, auto-indentation, project file tree, and live execution panel.
7. **HPM (HAKAI Package Manager)**: Manifest-based (`hakai.toml`) package management, dependency resolution, lockfile creation (`hakai.lock`), and local caching.

---

## Installation & Distribution

HAKAI can be installed either via Python's package manager (`pip`) directly from PyPI or as a standalone executable (no Python installation required).

### Method A: Python Package Distribution (`pip`)

HAKAI is officially published on PyPI as [**`hakai-lang`**](https://pypi.org/project/hakai-lang/). Requires Python 3.10+:

```bash
# Core language toolchain, compiler, VM, and HPM CLI (~35 KB wheel)
pip install hakai-lang

# Optional: with HAKAI Studio desktop IDE (PySide6 / Qt6)
pip install "hakai-lang[studio]"
```

Verify your installation:
```bash
hakai --version
# HAKAI Programming Language v1.0.0

hpm --version
# HAKAI Package Manager (HPM) v1.0.0
```

### Method B: Standalone Public Installers (No Python Required)

Download pre-built standalone binaries from the [GitHub Releases](https://github.com/Midhunesh14/HAKAI/releases) page:

- **Windows 10/11 (64-bit)**:
  - `HAKAI-1.0.0-Windows-x64-Portable.zip`: Standalone `hakai.exe`, `hpm.exe`, stdlib, and examples.
  - `HAKAI-1.0.0-Windows-Installer.bat`: One-click setup script that installs to `%LOCALAPPDATA%\HAKAI` and configures `PATH`.
  - `HAKAI-Studio-1.0.0-Windows-x64.zip`: Standalone HAKAI Studio desktop IDE executable.
- **Linux (x86_64)**:
  - `HAKAI-1.0.0-Linux-x64.tar.gz`: Self-contained `hakai` and `hpm` executables.
- **macOS (Intel / Apple Silicon)**:
  - `HAKAI-1.0.0-macOS-universal.tar.gz`: Self-contained `hakai` and `hpm` executables.

Detailed instructions, PATH setup, and checksum verification are available in the [Installation Guide](docs/INSTALLATION.md).

---

## Quick Start

### 1. Running a HAKAI Script
Create a file named `hello.hakai`:
```hakai
HAKAI START

let greeting = "Hello from HAKAI!"
print(greeting)

HAKAI END
```

Execute using the interpreter:
```bash
hakai run hello.hakai
```

### 2. Compiling to Bytecode & Running on the VM
Compile the source file into `.hbc` bytecode:
```bash
hakai build hello.hakai
```

Execute the compiled bytecode with the HAKAI Virtual Machine (HVM):
```bash
hakai run hello.hbc
```

### 3. Syntax & Semantic Static Check
```bash
hakai check hello.hakai
```

### 4. Interactive REPL
```bash
hakai repl
```
```
HAKAI Interactive REPL v1.0.0
Type 'exit' or press Ctrl+C to quit.

>>> let x = 10
>>> let y = 20
>>> print(x + y)
30
```

### 5. Launch HAKAI Studio Desktop IDE
```bash
hakai studio
```
*(Requires `pip install "hakai-lang[studio]"` or the standalone Studio bundle).*

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

### Loops & Repetitions
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

print(math.sqrt(144))         // 12.0
print(strings.upper("hakai")) // HAKAI
```

---

## HPM (HAKAI Package Manager)

Initialize a new project manifest:
```bash
hpm init my_project
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

Install project dependencies:
```bash
hpm install
```

List installed packages:
```bash
hpm list
```

---

## Documentation

Full language and toolchain documentation is available in [`docs/`](docs/):
- [Installation Guide](docs/INSTALLATION.md)
- [Getting Started Guide](docs/GETTING_STARTED.md)
- [Language Specification](docs/LANGUAGE_SPECIFICATION.md)
- [Syntax Reference](docs/SYNTAX.md)
- [Functions Guide](docs/FUNCTIONS.md)
- [Object-Oriented Programming](docs/OOP.md)
- [Module System](docs/MODULES.md)
- [Compiler & VM Architecture](docs/COMPILER.md)
- [Standard Library Reference](docs/STANDARD_LIBRARY.md)
- [HPM Package Manager](docs/PACKAGE_MANAGER.md)
- [FAQ](docs/FAQ.md)

---

## Development & Testing

Clone the repository and install in editable mode:
```bash
git clone https://github.com/Midhunesh14/HAKAI.git
cd HAKAI
pip install -e ".[dev,studio]"
```

Run test suite:
```bash
python -m pytest tests/ -v
```

Build wheels and check packages:
```bash
python -m build
python -m twine check dist/*
```

---

## License
HAKAI is released under the [MIT License](LICENSE).
