# Frequently Asked Questions (FAQ)

### What is HAKAI?
HAKAI is an independent, general-purpose programming language designed to provide clean syntax, intuitive semantics, high-quality developer tooling, both interpreter and bytecode VM execution pipelines, and a desktop IDE.

### Does HAKAI translate source code into Python?
No. HAKAI implements its own lexical scanner, recursive-descent parser, AST node definitions, tree-walk interpreter, semantic analyzer, optimizer, bytecode generator, and virtual machine. It does not use Python `eval()` or `exec()`.

### How do I run a HAKAI script?
```bash
python main.py run my_script.hakai
```

### Can I compile HAKAI to bytecode?
Yes:
```bash
python main.py build my_script.hakai
python main.py run my_script.hbc
```

