# HAKAI Changelog

All notable changes to the HAKAI language and toolchain will be documented in this file.

## [1.0.0] - 2026-11-03

### Initial Release of HAKAI
- **Lexer & Scanner**:
  - Full UTF-8 support with line and column tracking.
  - Program boundary support (`HAKAI START` / `HAKAI END`).
  - Single-line (`//`) and multi-line (`/* ... */`) comments.
  - Escape sequences in strings (`\n`, `\t`, `\r`, `\\`, `\"`, `\'`).
- **Parser & AST**:
  - Recursive-descent parser with complete operator precedence hierarchy.
  - Variable and constant declarations (`let`, `const`).
  - Control flow: `if`, `else if`, `else`, `while`, `repeat`, `break`, `continue`.
  - First-class functions with closures, default parameters, and recursion.
  - Full Object-Oriented Programming: classes, single inheritance (`extends`), constructors (`init`), methods, static methods, and `self` dynamic dispatch.
  - Data collections: dynamic arrays, maps, and tuples.
- **Tree-Walk Interpreter & Runtime**:
  - Scoped lexical environments with constant immutability checks.
  - Builtin functions (`print`, `println`, `type`, `len`, `str`, `int`, `float`, `bool`, `range`, `open`).
  - Standard library modules (`math`, `strings`, `collections`, `files`, `io`, `system`).
- **HAKAI Compiler & Virtual Machine (HVM)**:
  - Semantic Analyzer for static symbol validation and scope analysis.
  - Constant folding and dead-code elimination optimizer.
  - Bytecode generator emitting portable bytecode objects.
  - Stack-based HAKAI Virtual Machine (HVM) with call stack and execution frames.
  - Binary bytecode file format (`.hbc`) with `HBC\x01` magic header.
- **Developer Tooling & Ecosystem**:
  - **HAKAI Studio**: Desktop IDE built with PySide6, featuring custom dark theme, syntax highlighter, code editor with gutter line numbers and auto-indent, project file explorer, and live execution console.
  - **HPM (HAKAI Package Manager)**: Project manifest (`hakai.toml`), dependency resolver, lockfile generator (`hakai.lock`), local package cache, and CLI (`hpm init`, `hpm install`, `hpm list`, `hpm uninstall`).
  - **HAKAI CLI**: Integrated toolchain CLI with `run`, `build`, `check`, `repl`, `new`, `format`, `studio`, and `version`.
- **Testing & Quality Assurance**:
  - 37 unit and integration tests with 100% pass rate.
  - Validated semantic equivalence between AST interpreter and bytecode VM.

