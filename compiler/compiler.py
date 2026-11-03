"""Compiler Driver for HAKAI Language."""

from __future__ import annotations

import os
from typing import Optional
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.optimizer import ASTOptimizer
from compiler.bytecode_generator import BytecodeGenerator
from virtual_machine.instructions import HakaiCodeObject


class Compiler:
    """Orchestrates lexing, parsing, semantic analysis, optimization, and bytecode generation."""

    def __init__(self) -> None:
        self.optimizer = ASTOptimizer()
        self.analyzer = SemanticAnalyzer()

    def compile(self, source: str, filename: str = "<source>") -> HakaiCodeObject:
        """Compile HAKAI source code into a HakaiCodeObject."""
        # 1. Lex
        tokens = Lexer(source=source, filename=filename).tokenize()

        # 2. Parse
        ast = Parser(tokens=tokens, source_code=source).parse()

        # 3. Semantic Analysis
        self.analyzer.analyze(ast)

        # 4. Optimization
        opt_ast = self.optimizer.optimize(ast)

        # 5. Bytecode Generation
        generator = BytecodeGenerator(unit_name=filename)
        return generator.generate(opt_ast)

    def compile_to_file(
        self,
        source_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Compile a .hakai source file into a .hbc bytecode file."""
        if not output_path:
            base, _ = os.path.splitext(source_path)
            output_path = f"{base}.hbc"

        with open(source_path, "r", encoding="utf-8") as f:
            source = f.read()

        code_obj = self.compile(source, filename=source_path)
        data = code_obj.serialize()

        with open(output_path, "wb") as f:
            f.write(data)

        return output_path

