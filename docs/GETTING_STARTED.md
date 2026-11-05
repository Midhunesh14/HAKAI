# Getting Started with HAKAI

HAKAI is a modern, independent programming language featuring an AST-based tree-walk interpreter, optimizing bytecode compiler, virtual machine (`HVM`), package manager (`HPM`), and IDE (`HAKAI Studio`).

---

## 1. Quick Installation

### Python Package (Recommended for Python users)
```bash
# Core language toolchain and HPM CLI
pip install hakai-lang

# With HAKAI Studio GUI IDE
pip install "hakai-lang[studio]"
```

### Standalone Executable (No Python required)
Download the standalone installer or portable zip for Windows, Linux, or macOS from [GitHub Releases](https://github.com/Midhunesh14/HAKAI/releases).

For complete installation steps, PATH setup, and troubleshooting, see the [Installation Guide](INSTALLATION.md).

---

## 2. Verifying the Toolchain

After installation, verify both commands are available:
```bash
hakai --version
hpm --version
```

---

## 3. Your First Program

Create a file named `hello.hakai`:
```hakai
HAKAI START

let greeting = "Hello, HAKAI World!"
print(greeting)

HAKAI END
```

### Run with the AST Interpreter
```bash
hakai run hello.hakai
```
Output:
```
Hello, HAKAI World!
```

### Compile to Bytecode and Run on the VM
Compile the source to `.hbc` bytecode:
```bash
hakai build hello.hakai
```
Execute the compiled binary on the HAKAI Virtual Machine (HVM):
```bash
hakai run hello.hbc
```

---

## 4. Interactive REPL

Experiment with language expressions and statements in the interactive shell:
```bash
hakai repl
```
```
HAKAI Interactive REPL v1.0.0
Type 'exit' or press Ctrl+C to quit.

>>> let name = "Developer"
>>> print("Hello " + name + "!")
Hello Developer!
>>> 2 ** 8
256.0
```

---

## 5. Next Steps

- [Installation Guide](INSTALLATION.md)
- [Language Specification](LANGUAGE_SPECIFICATION.md)
- [Syntax Reference](SYNTAX.md)
- [Functions Guide](FUNCTIONS.md)
- [Object-Oriented Programming](OOP.md)
- [Module System](MODULES.md)
- [Compiler & VM Architecture](COMPILER.md)
- [Standard Library Reference](STANDARD_LIBRARY.md)
- [HPM Package Manager](PACKAGE_MANAGER.md)
