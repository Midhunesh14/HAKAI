# HAKAI Project Roadmap

## Phase 1: Core Language Design & Frontend (Milestones 1 - 3)
- [x] Workspace inspection and structural setup
- [ ] M1: Formal Language Specification (`LANGUAGE_SPECIFICATION.md`, `SYNTAX.md`)
- [ ] M2: Lexer & Tokenizer implementation (`compiler/lexer.py`, `compiler/tokens.py`)
- [ ] M3: AST Nodes & Recursive-Descent Parser (`compiler/ast_nodes.py`, `compiler/parser.py`)

## Phase 2: Runtime & Core Semantics (Milestones 4 - 8)
- [ ] M4: Tree-Walk Interpreter, Scopes & Evaluation (`interpreter/interpreter.py`, `interpreter/environment.py`)
- [ ] M5: Type System, Literals, Operators (`interpreter/values.py`)
- [ ] M6: Control Flow (`if`, `else if`, `else`, `while`, `repeat`, `break`, `continue`)
- [ ] M7: First-Class Functions & Full OOP (`interpreter/functions.py`, `interpreter/classes.py`)
- [ ] M8: Standard Library & Safe IO/System Modules (`stdlib/`, `interpreter/runtime.py`)

## Phase 3: Compilation, Virtual Machine & Performance (Milestone 9)
- [ ] M9.1: Semantic Analyzer & Symbol Table (`compiler/semantic_analyzer.py`)
- [ ] M9.2: Intermediate Representation (IR) (`compiler/intermediate_representation.py`)
- [ ] M9.3: Constant Folding & IR Optimizer (`compiler/optimizer.py`)
- [ ] M9.4: Stack-based Bytecode Generator (`compiler/bytecode_generator.py`)
- [ ] M9.5: Virtual Machine (`virtual_machine/vm.py`, `virtual_machine/execution.py`, `virtual_machine/instructions.py`)
- [ ] M9.6: Bytecode file serialization (`.hbc`)

## Phase 4: Developer Tooling & Ecosystem (Milestones 10 - 12)
- [ ] M10: HAKAI Studio Desktop IDE (PySide6 with editor, syntax highlighter, explorer, console)
- [ ] M11: HPM Package Manager (`package_manager/`)
- [ ] M12: CLI, Interactive REPL, Windows installer scripts, Full Documentation & 1.0 Release
