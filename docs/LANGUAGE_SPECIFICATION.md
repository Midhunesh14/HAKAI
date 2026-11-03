# HAKAI Language Specification v1.0.0

## 1. Overview
HAKAI is a strongly typed, dynamically checked, object-oriented, imperative, general-purpose programming language. It is designed for clarity, safety, expressive syntax, and robust compilation to portable bytecode.

## 2. Lexical Structure

### 2.1 Characters & Encodings
HAKAI source files are UTF-8 encoded text files. By convention, files use the `.hakai` extension.

### 2.2 Whitespace
Whitespace (spaces, tabs, newlines) serves as token separators and is otherwise ignored outside string literals. Semicolons are optional statement separators.

### 2.3 Comments
- Single-line comments start with `//` and extend to the end of the line.
- Multi-line comments start with `/*` and terminate with `*/`. Multi-line comments may span multiple lines.

```hakai
// Single-line comment
/*
   Multi-line
   comment
*/
```

### 2.4 Program Boundaries
Every HAKAI program may optionally begin with `HAKAI START` and terminate with `HAKAI END`. When present, all executable statements must reside within these boundaries:

```hakai
HAKAI START
print("Hello World!")
HAKAI END
```
For modular scripts or files intended to be imported as libraries, `HAKAI START` and `HAKAI END` are optional to allow natural top-level definitions.

### 2.5 Identifiers & Keywords
Identifiers start with an ASCII letter or underscore `[a-zA-Z_]` followed by any combination of letters, digits, and underscores `[a-zA-Z0-9_]*`.

Reserved keywords cannot be used as variable or function names:
`let`, `const`, `if`, `else`, `elseif`, `while`, `repeat`, `break`, `continue`, `return`, `function`, `class`, `extends`, `static`, `self`, `super`, `import`, `from`, `as`, `export`, `and`, `or`, `not`, `in`, `is`, `true`, `false`, `null`, `try`, `catch`, `finally`, `throw`, `for`, `foreach`, `new`.

### 2.6 Literals
- **Integer**: Sequence of decimal digits, e.g. `42`, `0`, `1000`. Supports negative integers via unary minus `-5`.
- **Float**: Digits with a decimal point and optional exponent, e.g. `3.14159`, `0.5`, `1.0e-3`.
- **String**: Enclosed in double quotes `"..."` or single quotes `'...'`. Supports escape sequences `\n`, `\t`, `\r`, `\\`, `\"`, `\'`. String interpolation is supported via `{variable}` or format expressions inside strings.
- **Boolean**: `true` or `false`.
- **Null**: `null`.
- **Array**: `[1, 2, "three", true]`.
- **Map / Dictionary**: `{"key": "value", "count": 10}`.
- **Tuple**: `(1, 2, 3)` (comma-delimited in parentheses).

---

## 3. Variables and Constants

### 3.1 Mutable Variables (`let`)
Declared with the `let` keyword:
```hakai
let message = "Welcome"
let count = 0
count = count + 1
```

### 3.2 Constants (`const`)
Declared with the `const` keyword. Reassigning to a `const` identifier generates a compile/runtime error:
```hakai
const PI = 3.1415926535
const APP_NAME = "HAKAI Engine"
```

---

## 4. Operators and Expressions

### 4.1 Operator Precedence (Lowest to Highest)
1. Assignment: `=`
2. Logical OR: `or`
3. Logical AND: `and`
4. Equality: `==`, `!=`
5. Relational: `<`, `<=`, `>`, `>=`
6. Additive: `+`, `-`
7. Multiplicative: `*`, `/`, `%`
8. Exponential: `**`
9. Unary: `not`, `-`, `+`
10. Call, Member Access, Subscript: `()`, `.`, `[]`

---

## 5. Control Flow

### 5.1 Conditional Statements
```hakai
if score >= 90 {
    print("Grade: A")
} else if score >= 80 {
    print("Grade: B")
} else {
    print("Grade: C")
}
```

### 5.2 Loops
#### While Loop
```hakai
let counter = 0
while counter < 5 {
    print(counter)
    counter = counter + 1
}
```

#### Repeat Loop
Iterates a fixed count $N$ times:
```hakai
repeat 3 {
    print("HAKAI!")
}
```

#### Loop Controls
`break` terminates the enclosing loop; `continue` skips to the next iteration.

---

## 6. Functions

### 6.1 Function Definition and Invocation
```hakai
function multiply(x, y) {
    return x * y
}

let result = multiply(6, 7)
```

### 6.2 Default Parameters
```hakai
function greet(name, greeting = "Hello") {
    return greeting + ", " + name + "!"
}
```

### 6.3 Closures & First-Class Functions
Functions capture their enclosing lexical environment and can be stored in variables or passed as arguments:
```hakai
function makeAdder(amount) {
    function adder(x) {
        return x + amount
    }
    return adder
}
let add5 = makeAdder(5)
print(add5(10)) // 15
```

---

## 7. Object-Oriented Programming

### 7.1 Class Definition
```hakai
class Person {
    function init(name, age) {
        self.name = name
        self.age = age
    }

    function describe() {
        return self.name + " is " + str(self.age) + " years old"
    }

    static function species() {
        return "Homo sapiens"
    }
}
```

### 7.2 Instantiation & Method Calls
```hakai
let p = Person("Alice", 25)
print(p.describe())
print(Person.species())
```

### 7.3 Inheritance & Method Overriding
```hakai
class Employee extends Person {
    function init(name, age, role) {
        self.name = name
        self.age = age
        self.role = role
    }

    function describe() {
        return self.name + " works as " + self.role
    }
}
```

---

## 8. Modules & Standard Library

### 8.1 Imports
```hakai
import math
import strings as str_tools
from io import println
```

### 8.2 Standard Modules
- `math`: `sqrt`, `pow`, `abs`, `floor`, `ceil`, `sin`, `cos`, `pi`, `e`
- `strings`: `upper`, `lower`, `trim`, `split`, `join`, `replace`, `contains`, `starts_with`, `ends_with`
- `collections`: `push`, `pop`, `insert`, `remove`, `slice`, `keys`, `values`, `has_key`
- `files`: `read_text`, `write_text`, `append_text`, `exists`, `delete`, `open`
- `io`: `print`, `println`, `input`, `read_line`
- `system`: `time`, `sleep`, `platform`, `version`, `exit`, `args`

---

## 9. Error Diagnostics
All compiler and runtime errors provide precise source attribution:
```
HAKAI Syntax Error:
hello.hakai:5:12
Unexpected token: )
Expected an expression.
```

