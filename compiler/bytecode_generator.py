"""Bytecode Generator for HAKAI Compiler."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from compiler.ast_nodes import (
    ASTNode,
    ASTVisitor,
    Program,
    Block,
    VarDecl,
    FunctionDecl,
    ClassDecl,
    IfStmt,
    WhileStmt,
    RepeatStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    ExpressionStmt,
    Literal,
    Identifier,
    SelfNode,
    SuperNode,
    Assign,
    Binary,
    Unary,
    Call,
    Get,
    Set as AstSet,
    Index,
    IndexSet,
    ArrayLiteral,
    MapLiteral,
    TupleLiteral,
)
from virtual_machine.instructions import HakaiCodeObject, Instruction, Opcode


class BytecodeGenerator(ASTVisitor):
    """Compiles HAKAI AST into a flat HakaiCodeObject."""

    def __init__(self, unit_name: str = "<main>") -> None:
        self.unit_name = unit_name
        self.constants: List[Any] = []
        self.names: List[str] = []
        self.instructions: List[Instruction] = []
        self.loop_starts: List[int] = []
        self.loop_breaks: List[List[int]] = []

    def generate(self, program: Program) -> HakaiCodeObject:
        self.visit_Program(program)
        # Emit terminal HALT instruction
        self._emit(Opcode.HALT, line=program.line)
        return HakaiCodeObject(
            name=self.unit_name,
            constants=self.constants,
            names=self.names,
            instructions=self.instructions,
        )

    # -------------------------------------------------------------------------
    # Helper management
    # -------------------------------------------------------------------------

    def _add_const(self, value: Any) -> int:
        for idx, c in enumerate(self.constants):
            if type(c) == type(value) and c == value:
                return idx
        self.constants.append(value)
        return len(self.constants) - 1

    def _add_name(self, name: str) -> int:
        if name in self.names:
            return self.names.index(name)
        self.names.append(name)
        return len(self.names) - 1

    def _emit(self, opcode: Opcode, operand: Optional[int] = None, line: int = 1) -> int:
        idx = len(self.instructions)
        self.instructions.append(Instruction(opcode=opcode, operand=operand, line=line))
        return idx

    def _patch(self, instruction_index: int, target: int) -> None:
        self.instructions[instruction_index].operand = target

    # -------------------------------------------------------------------------
    # Statement compilation
    # -------------------------------------------------------------------------

    def visit_Program(self, node: Program) -> None:
        for stmt in node.statements:
            stmt.accept(self)

    def visit_Block(self, node: Block) -> None:
        for stmt in node.statements:
            stmt.accept(self)

    def visit_VarDecl(self, node: VarDecl) -> None:
        if node.initializer is not None:
            node.initializer.accept(self)
        else:
            c_idx = self._add_const(None)
            self._emit(Opcode.LOAD_CONST, c_idx, line=node.line)

        name_idx = self._add_name(node.name)
        self._emit(Opcode.STORE_NAME, name_idx, line=node.line)

    def visit_ExpressionStmt(self, node: ExpressionStmt) -> None:
        node.expression.accept(self)
        # Clean expression results off stack
        self._emit(Opcode.POP, line=node.line)

    def visit_IfStmt(self, node: IfStmt) -> None:
        node.condition.accept(self)
        jump_false_idx = self._emit(Opcode.JUMP_IF_FALSE, line=node.line)

        node.then_branch.accept(self)

        if node.else_branch is not None:
            jump_end_idx = self._emit(Opcode.JUMP, line=node.line)
            # Target of jump_if_false is start of else branch
            self._patch(jump_false_idx, len(self.instructions))
            node.else_branch.accept(self)
            self._patch(jump_end_idx, len(self.instructions))
        else:
            self._patch(jump_false_idx, len(self.instructions))

    def visit_WhileStmt(self, node: WhileStmt) -> None:
        loop_start = len(self.instructions)
        self.loop_starts.append(loop_start)
        self.loop_breaks.append([])

        node.condition.accept(self)
        jump_false_idx = self._emit(Opcode.JUMP_IF_FALSE, line=node.line)

        node.body.accept(self)
        self._emit(Opcode.JUMP, loop_start, line=node.line)

        loop_end = len(self.instructions)
        self._patch(jump_false_idx, loop_end)

        # Patch break jumps
        breaks = self.loop_breaks.pop()
        self.loop_starts.pop()
        for b_idx in breaks:
            self._patch(b_idx, loop_end)

    def visit_RepeatStmt(self, node: RepeatStmt) -> None:
        # Compile repeat N { body }
        # Evaluate count and store in anonymous temp
        node.count.accept(self)
        temp_name = f"__repeat_{len(self.instructions)}"
        name_idx = self._add_name(temp_name)
        self._emit(Opcode.STORE_NAME, name_idx, line=node.line)

        loop_start = len(self.instructions)
        self.loop_starts.append(loop_start)
        self.loop_breaks.append([])

        # Check temp > 0
        self._emit(Opcode.LOAD_NAME, name_idx, line=node.line)
        zero_idx = self._add_const(0)
        self._emit(Opcode.LOAD_CONST, zero_idx, line=node.line)
        self._emit(Opcode.COMPARE_GT, line=node.line)
        jump_false_idx = self._emit(Opcode.JUMP_IF_FALSE, line=node.line)

        node.body.accept(self)

        # Decrement temp: temp = temp - 1
        self._emit(Opcode.LOAD_NAME, name_idx, line=node.line)
        one_idx = self._add_const(1)
        self._emit(Opcode.LOAD_CONST, one_idx, line=node.line)
        self._emit(Opcode.SUB, line=node.line)
        self._emit(Opcode.STORE_NAME, name_idx, line=node.line)

        self._emit(Opcode.JUMP, loop_start, line=node.line)

        loop_end = len(self.instructions)
        self._patch(jump_false_idx, loop_end)
        breaks = self.loop_breaks.pop()
        self.loop_starts.pop()
        for b_idx in breaks:
            self._patch(b_idx, loop_end)

    def visit_BreakStmt(self, node: BreakStmt) -> None:
        idx = self._emit(Opcode.JUMP, line=node.line)
        if self.loop_breaks:
            self.loop_breaks[-1].append(idx)

    def visit_ContinueStmt(self, node: ContinueStmt) -> None:
        if self.loop_starts:
            self._emit(Opcode.JUMP, self.loop_starts[-1], line=node.line)

    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        if node.value is not None:
            node.value.accept(self)
        else:
            c_idx = self._add_const(None)
            self._emit(Opcode.LOAD_CONST, c_idx, line=node.line)
        self._emit(Opcode.RETURN, line=node.line)

    def visit_FunctionDecl(self, node: FunctionDecl) -> None:
        # Function compiled as separate code object
        fn_gen = BytecodeGenerator(unit_name=node.name)
        param_names = [p.name for p in node.params]
        for p_name in param_names:
            fn_gen._add_name(p_name)
        node.body.accept(fn_gen)
        # Default return None if no explicit return
        none_idx = fn_gen._add_const(None)
        fn_gen._emit(Opcode.LOAD_CONST, none_idx, line=node.line)
        fn_gen._emit(Opcode.RETURN, line=node.line)

        code_obj = HakaiCodeObject(
            name=node.name,
            constants=fn_gen.constants,
            names=fn_gen.names,
            instructions=fn_gen.instructions,
            param_names=param_names,
        )
        c_idx = self._add_const(code_obj)
        self._emit(Opcode.LOAD_CONST, c_idx, line=node.line)
        name_idx = self._add_name(node.name)
        self._emit(Opcode.STORE_NAME, name_idx, line=node.line)

    # -------------------------------------------------------------------------
    # Expression compilation
    # -------------------------------------------------------------------------

    def visit_Literal(self, node: Literal) -> None:
        c_idx = self._add_const(node.value)
        self._emit(Opcode.LOAD_CONST, c_idx, line=node.line)

    def visit_Identifier(self, node: Identifier) -> None:
        name_idx = self._add_name(node.name)
        self._emit(Opcode.LOAD_NAME, name_idx, line=node.line)

    def visit_Assign(self, node: Assign) -> None:
        node.value.accept(self)
        name_idx = self._add_name(node.name)
        self._emit(Opcode.STORE_NAME, name_idx, line=node.line)
        # Assignment expressions evaluate to the assigned value
        self._emit(Opcode.LOAD_NAME, name_idx, line=node.line)

    def visit_Binary(self, node: Binary) -> None:
        node.left.accept(self)
        node.right.accept(self)

        op = node.operator
        line = node.line
        if op == "+":
            self._emit(Opcode.ADD, line=line)
        elif op == "-":
            self._emit(Opcode.SUB, line=line)
        elif op == "*":
            self._emit(Opcode.MUL, line=line)
        elif op == "/":
            self._emit(Opcode.DIV, line=line)
        elif op == "%":
            self._emit(Opcode.MOD, line=line)
        elif op == "**":
            self._emit(Opcode.POW, line=line)
        elif op == "==":
            self._emit(Opcode.COMPARE_EQ, line=line)
        elif op == "!=":
            self._emit(Opcode.COMPARE_NE, line=line)
        elif op == "<":
            self._emit(Opcode.COMPARE_LT, line=line)
        elif op == "<=":
            self._emit(Opcode.COMPARE_LE, line=line)
        elif op == ">":
            self._emit(Opcode.COMPARE_GT, line=line)
        elif op == ">=":
            self._emit(Opcode.COMPARE_GE, line=line)

    def visit_Unary(self, node: Unary) -> None:
        node.operand.accept(self)
        if node.operator in ("not", "!"):
            self._emit(Opcode.UNARY_NOT, line=node.line)
        elif node.operator == "-":
            self._emit(Opcode.UNARY_NEG, line=node.line)

    def visit_Call(self, node: Call) -> None:
        # Evaluate callee
        node.callee.accept(self)
        # Evaluate arguments
        for arg in node.arguments:
            arg.accept(self)
        self._emit(Opcode.CALL, len(node.arguments), line=node.line)

    def visit_ClassDecl(self, node: ClassDecl) -> None:
        methods = {}
        for m in node.methods:
            m_gen = BytecodeGenerator(unit_name=f"{node.name}.{m.name}")
            p_names = [p.name for p in m.params]
            for p in p_names:
                m_gen._add_name(p)
            m.body.accept(m_gen)
            none_idx = m_gen._add_const(None)
            m_gen._emit(Opcode.LOAD_CONST, none_idx, line=m.line)
            m_gen._emit(Opcode.RETURN, line=m.line)
            methods[m.name] = HakaiCodeObject(
                name=f"{node.name}.{m.name}",
                constants=m_gen.constants,
                names=m_gen.names,
                instructions=m_gen.instructions,
                param_names=p_names,
            )

        static_methods = {}
        for sm in node.static_methods:
            sm_gen = BytecodeGenerator(unit_name=f"{node.name}.{sm.name}")
            p_names = [p.name for p in sm.params]
            for p in p_names:
                sm_gen._add_name(p)
            sm.body.accept(sm_gen)
            none_idx = sm_gen._add_const(None)
            sm_gen._emit(Opcode.LOAD_CONST, none_idx, line=sm.line)
            sm_gen._emit(Opcode.RETURN, line=sm.line)
            static_methods[sm.name] = HakaiCodeObject(
                name=f"{node.name}.{sm.name}",
                constants=sm_gen.constants,
                names=sm_gen.names,
                instructions=sm_gen.instructions,
                param_names=p_names,
            )

        class_data = {
            "name": node.name,
            "superclass": node.superclass,
            "methods": methods,
            "static_methods": static_methods,
        }
        c_idx = self._add_const(class_data)
        self._emit(Opcode.BUILD_CLASS, c_idx, line=node.line)
        name_idx = self._add_name(node.name)
        self._emit(Opcode.STORE_NAME, name_idx, line=node.line)

    def visit_ImportStmt(self, node: ImportStmt) -> None:
        name_idx = self._add_name(node.module_name)
        self._emit(Opcode.IMPORT_MODULE, name_idx, line=node.line)
        target = node.alias or node.module_name
        target_idx = self._add_name(target)
        self._emit(Opcode.STORE_NAME, target_idx, line=node.line)

    def visit_ArrayLiteral(self, node: ArrayLiteral) -> None:
        for elem in node.elements:
            elem.accept(self)
        self._emit(Opcode.BUILD_ARRAY, len(node.elements), line=node.line)

    def visit_TupleLiteral(self, node: TupleLiteral) -> None:
        for elem in node.elements:
            elem.accept(self)
        self._emit(Opcode.BUILD_ARRAY, len(node.elements), line=node.line)

    def visit_SelfNode(self, node: SelfNode) -> None:
        name_idx = self._add_name("self")
        self._emit(Opcode.LOAD_NAME, name_idx, line=node.line)

    def visit_SuperNode(self, node: SuperNode) -> None:
        name_idx = self._add_name("self")
        self._emit(Opcode.LOAD_NAME, name_idx, line=node.line)
        meth_idx = self._add_name(node.method)
        self._emit(Opcode.GET_ATTR, meth_idx, line=node.line)
        for elem in node.elements:
            elem.accept(self)
        self._emit(Opcode.BUILD_ARRAY, len(node.elements), line=node.line)

    def visit_MapLiteral(self, node: MapLiteral) -> None:
        for k, v in node.pairs:
            k.accept(self)
            v.accept(self)
        self._emit(Opcode.BUILD_MAP, len(node.pairs), line=node.line)

    def visit_Index(self, node: Index) -> None:
        node.target.accept(self)
        node.index.accept(self)
        self._emit(Opcode.GET_INDEX, line=node.line)

    def visit_IndexSet(self, node: IndexSet) -> None:
        node.target.accept(self)
        node.index.accept(self)
        node.value.accept(self)
        self._emit(Opcode.SET_INDEX, line=node.line)

    def visit_Get(self, node: Get) -> None:
        node.obj.accept(self)
        name_idx = self._add_name(node.name)
        self._emit(Opcode.GET_ATTR, name_idx, line=node.line)

    def visit_Set(self, node: AstSet) -> None:
        node.obj.accept(self)
        node.value.accept(self)
        name_idx = self._add_name(node.name)
        self._emit(Opcode.SET_ATTR, name_idx, line=node.line)
