# Getting Started with HAKAI

## Installation
HAKAI can be run directly using Python 3.10+ or installed via the provided installer script.

```bash
# Check version
python main.py version

# Run an example
python main.py run examples/hello.hakai

# Compile to bytecode
python main.py build examples/hello.hakai

# Run compiled bytecode
python main.py run examples/hello.hbc

# Launch HAKAI Studio IDE
python main.py studio
```

## First Program
Create a file named `hello.hakai`:
```hakai
HAKAI START

let greeting = "Hello, HAKAI World!"
print(greeting)

HAKAI END
```
Execute it:
```bash
python main.py run hello.hakai
```
Output:
```
Hello, HAKAI World!
```

