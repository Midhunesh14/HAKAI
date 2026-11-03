# HAKAI Compiler & Virtual Machine Architecture

The HAKAI toolchain includes both an interactive tree-walk interpreter for instant feedback and a bytecode compiler with a dedicated stack-based virtual machine (`HVM`).

## Pipeline
```
Source (.hakai)
   │
   ▼ [Lexer]
Token Stream
   │
   ▼ [Parser]
Abstract Syntax Tree (AST)
   │
   ▼ [Semantic Analyzer]
Annotated AST + Symbol Tables
   │
   ▼ [IR Lowering & Optimizer]
Intermediate Representation (IR) + Constant Folding
   │
   ▼ [Bytecode Generator]
HAKAI Bytecode Object (.hbc)
   │
   ▼ [Virtual Machine]
Stack-based Execution Engine
```

## Bytecode File Format (`.hbc`)
HAKAI bytecode files contain:
- Magic bytes: `HBC\x01`
- Version descriptor
- Constant pool (numbers, strings, booleans, code objects)
- Name table (identifiers)
- Instruction stream (opcode + operands)
- Source line-mapping table for debugging

## Virtual Machine Instructions
- `LOAD_CONST <index>`: Push constant from pool onto stack
- `LOAD_NAME <index>`: Push variable value by name
- `STORE_NAME <index>`: Store top of stack into named slot
- `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `POW`: Arithmetic on top operands
- `COMPARE <op>`: Comparison test (`==`, `!=`, `<`, `<=`, `>`, `>=`)
- `JUMP <target>`: Unconditional branch
- `JUMP_IF_FALSE <target>`: Conditional branch on falsy stack top
- `CALL <arg_count>`: Invoke callable
- `RETURN`: Return from current frame
- `POP`: Discard top of stack
- `HALT`: Terminate execution

