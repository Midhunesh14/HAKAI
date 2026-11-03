# Contributing to HAKAI

Thank you for your interest in contributing to the HAKAI programming language!

## Development Guidelines
1. **Modularity**: Never place unrelated features in single monolith files. Adhere to the frontend, runtime, compiler, and tooling boundaries.
2. **Type Annotations**: All Python code in HAKAI must have complete typing annotations.
3. **No External Simulators**: Features must execute through either the AST interpreter or the bytecode VM.
4. **Testing**: Every change must be accompanied by unit tests in `tests/`.
5. **Diagnostics**: Syntax and runtime errors must output clean location details (file, line, column, and context line).

## Running Tests
```bash
pytest tests/ -v
```

## Running the CLI
```bash
python main.py run examples/hello.hakai
```
