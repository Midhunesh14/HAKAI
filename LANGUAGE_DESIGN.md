# HAKAI Language Design Manifesto

## 1. Philosophy & Identity
HAKAI is designed to strike an optimal balance between human readability and mechanical precision.
- **Explicit Program Demarcation**: Optional or formal programs can begin with `HAKAI START` and terminate with `HAKAI END`.
- **Clean Block Syntax**: Braced blocks `{ ... }` eliminate ambiguity while retaining free-form expression layout.
- **Expressive Keywords**: Plain English control keywords (`repeat N`, `while`, `function`, `class`, `let`, `const`).
- **Safety by Default**: Strict lexical scoping, immutable constants via `const`, explicit variable declaration via `let`, and controlled sandboxing for filesystem/system APIs.
- **First-Class Everything**: Functions and classes are first-class values that can be passed, returned, stored in collections, and introspected.

## 2. Grammar Summary (EBNF-like)

```ebnf
Program        ::= ("HAKAI" "START")? Statement* ("HAKAI" "END")? EOF ;

Statement      ::= VarDecl
                 | ConstDecl
                 | FunctionDecl
                 | ClassDecl
                 | IfStmt
                 | WhileStmt
                 | RepeatStmt
                 | ReturnStmt
                 | BreakStmt
                 | ContinueStmt
                 | ImportStmt
                 | ExprStmt
                 | Block ;

VarDecl        ::= "let" IDENTIFIER ("=" Expression)? ;
ConstDecl      ::= "const" IDENTIFIER "=" Expression ;

FunctionDecl   ::= "function" IDENTIFIER "(" ParameterList? ")" Block ;
ParameterList  ::= IDENTIFIER ("=" Expression)? ("," IDENTIFIER ("=" Expression)?)* ;

ClassDecl      ::= "class" IDENTIFIER ("extends" IDENTIFIER)? "{" ClassMember* "}" ;
ClassMember    ::= ("static")? FunctionDecl ;

IfStmt         ::= "if" Expression Block ("else" "if" Expression Block | "elseif" Expression Block)* ("else" Block)? ;
WhileStmt      ::= "while" Expression Block ;
RepeatStmt     ::= "repeat" Expression Block ;

ReturnStmt     ::= "return" Expression? ;
BreakStmt      ::= "break" ;
ContinueStmt   ::= "continue" ;
ImportStmt     ::= "import" IDENTIFIER ("as" IDENTIFIER)?
                 | "from" IDENTIFIER "import" IDENTIFIER ("," IDENTIFIER)* ;

Block          ::= "{" Statement* "}" ;

Expression     ::= Assignment ;
Assignment     ::= (Call ".")? IDENTIFIER "=" Assignment
                 | Call "[" Expression "]" "=" Assignment
                 | LogicOr ;
LogicOr        ::= LogicAnd ("or" LogicAnd)* ;
LogicAnd       ::= Equality ("and" Equality)* ;
Equality       ::= Relational (("==" | "!=") Relational)* ;
Relational     ::= Additive (("<" | "<=" | ">" | ">=") Additive)* ;
Additive       ::= Multiplicative (("+" | "-") Multiplicative)* ;
Multiplicative ::= Exponential (("*" | "/" | "%") Exponential)* ;
Exponential    ::= Unary ("**" Exponential)? ;
Unary          ::= ("not" | "-" | "+") Unary | Primary ;
Call           ::= Primary ( "(" ArgumentList? ")" | "." IDENTIFIER | "[" Expression "]" )* ;
Primary        ::= INTEGER | FLOAT | STRING | BOOLEAN | "null"
                 | IDENTIFIER | "self" | "super"
                 | "[" (Expression ("," Expression)*)? "]"
                 | "{" (Expression ":" Expression ("," Expression ":" Expression)*)? "}"
                 | "(" Expression ")" ;
```

## 3. Scoping & Environments
1. Lexical block scoping: Each block `{}` creates a child environment.
2. Variable shadowing is permitted in inner blocks.
3. Accessing undefined variables raises a `HakaiNameError`.
4. Mutating `const` bindings raises a `HakaiTypeError`.

## 4. Object-Oriented Semantics
- Instances are created using class call syntax: `let s = Student("Alice", 20)`.
- Constructors are named `init(...)`.
- `self` binds explicitly to the calling instance.
- Single inheritance via `class Child extends Parent`.
- Virtual method dispatch with `super` access.

