# HAKAI System Architecture

```
+-------------------------------------------------------------------+
|                           HAKAI CLI / REPL                        |
|                     (hakai run / build / check / repl)            |
+-------------------------------------------------------------------+
                               |
             +-----------------+-----------------+
             |                                   |
             v                                   v
+------------------------+             +------------------------+
|      HAKAI Studio      |             |   HPM Package Manager  |
|  (PySide6 Desktop IDE) |             |  (hakai.toml manifests)|
+------------------------+             +------------------------+
             |                                   |
             +-----------------+-----------------+
                               |
                               v
               +-------------------------------+
               |     Lexer (tokens.py / lexer) |
               +-------------------------------+
                               |
                               v
               +-------------------------------+
               |    Parser (ast_nodes / parser)|
               +-------------------------------+
                               |
                               v
                         [ AST Root ]
                               |
         +---------------------+---------------------+
         |                                           |
         v                                           v
+------------------------+               +------------------------+
|   AST Interpreter      |               |   Semantic Analyzer    |
| - Environment & Scopes |               +------------------------+
| - Value System         |                           |
| - Native Builtins      |                           v
| - Standard Library     |               +------------------------+
+------------------------+               |   IR Generator & Opt   |
                                         +------------------------+
                                                     |
                                                     v
                                         +------------------------+
                                         |   Bytecode Generator   |
                                         |    (emits .hbc file)   |
                                         +------------------------+
                                                     |
                                                     v
                                         +------------------------+
                                         | HAKAI Virtual Machine  |
                                         | - Stack Engine         |
                                         | - Frame Call Stack     |
                                         | - Value Operations     |
                                         +------------------------+
```

## Directory Structure
- `compiler/`: Frontend pipeline (tokens, lexer, ast_nodes, parser, semantic_analyzer, intermediate_representation, optimizer, bytecode_generator, compiler driver)
- `interpreter/`: Direct tree-walk runtime engine (environment, values, functions, classes, exceptions, runtime)
- `virtual_machine/`: Stack-based virtual machine, instruction sets, bytecode loader, execution loops
- `stdlib/`: Built-in and standard libraries (`io`, `math`, `strings`, `collections`, `files`, `system`)
- `package_manager/`: HPM CLI tool and dependency resolver
- `cli/`: Command-line driver (`hakai`)
- `studio/`: Modern PySide6 desktop IDE with syntax highlighting, file tree, terminal, error markers
- `docs/`: Complete language documentation suite
- `examples/`: Canonical HAKAI programs demonstrating language features
- `tests/`: Extensive automated test suites across all modules
