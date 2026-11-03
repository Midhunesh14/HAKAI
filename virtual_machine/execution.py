"""Instruction dispatcher and execution engine for HAKAI Virtual Machine."""

from __future__ import annotations

from typing import Any, List
from compiler.errors import HakaiRuntimeError, HakaiTypeError, HakaiIndexError
from interpreter.values import is_truthy, hakai_to_str, hakai_type_name
from virtual_machine.instructions import HakaiCodeObject, Instruction, Opcode
from virtual_machine.memory import CallStack, Frame


class ExecutionEngine:
    """Executes bytecode instructions across the call stack."""

    def __init__(self, vm: Any, call_stack: CallStack) -> None:
        self.vm = vm
        self.call_stack = call_stack

    def step(self) -> bool:
        """Execute a single instruction in the current frame. Returns False when halted."""
        if self.call_stack.is_empty():
            return False

        frame = self.call_stack.current()
        if frame.ip >= len(frame.code.instructions):
            self.call_stack.pop()
            return not self.call_stack.is_empty()

        ins = frame.code.instructions[frame.ip]
        frame.ip += 1

        op = ins.opcode
        arg = ins.operand
        line = ins.line

        # ---------------------------------------------------------------------
        # Load & Store
        # ---------------------------------------------------------------------
        if op == Opcode.LOAD_CONST:
            val = frame.code.constants[arg]
            frame.push(val)

        elif op == Opcode.LOAD_NAME:
            name = frame.code.names[arg]
            if name in frame.locals:
                frame.push(frame.locals[name])
            elif name in frame.globals:
                frame.push(frame.globals[name])
            elif name in self.vm.builtins:
                frame.push(self.vm.builtins[name])
            else:
                raise HakaiRuntimeError(
                    f"Undefined variable '{name}' in bytecode execution (line {line})."
                )

        elif op == Opcode.STORE_NAME:
            name = frame.code.names[arg]
            val = frame.pop()
            frame.locals[name] = val
            # If top-level frame, also reflect in globals
            if len(self.call_stack.frames) == 1:
                frame.globals[name] = val

        # ---------------------------------------------------------------------
        # Arithmetic
        # ---------------------------------------------------------------------
        elif op == Opcode.ADD:
            b = frame.pop()
            a = frame.pop()
            if isinstance(a, str) or isinstance(b, str):
                frame.push(hakai_to_str(a) + hakai_to_str(b))
            elif isinstance(a, list) and isinstance(b, list):
                frame.push(a + b)
            elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
                frame.push(a + b)
            else:
                raise HakaiTypeError(f"Cannot add {hakai_type_name(a)} and {hakai_type_name(b)}.")

        elif op == Opcode.SUB:
            b = frame.pop()
            a = frame.pop()
            frame.push(a - b)

        elif op == Opcode.MUL:
            b = frame.pop()
            a = frame.pop()
            frame.push(a * b)

        elif op == Opcode.DIV:
            b = frame.pop()
            a = frame.pop()
            if b == 0:
                raise HakaiRuntimeError("Division by zero in VM.")
            frame.push(a / b)

        elif op == Opcode.MOD:
            b = frame.pop()
            a = frame.pop()
            if b == 0:
                raise HakaiRuntimeError("Modulo by zero in VM.")
            frame.push(a % b)

        elif op == Opcode.POW:
            b = frame.pop()
            a = frame.pop()
            frame.push(a**b)

        # ---------------------------------------------------------------------
        # Comparison & Unary
        # ---------------------------------------------------------------------
        elif op == Opcode.COMPARE_EQ:
            b = frame.pop()
            a = frame.pop()
            frame.push(a == b)

        elif op == Opcode.COMPARE_NE:
            b = frame.pop()
            a = frame.pop()
            frame.push(a != b)

        elif op == Opcode.COMPARE_LT:
            b = frame.pop()
            a = frame.pop()
            frame.push(a < b)

        elif op == Opcode.COMPARE_LE:
            b = frame.pop()
            a = frame.pop()
            frame.push(a <= b)

        elif op == Opcode.COMPARE_GT:
            b = frame.pop()
            a = frame.pop()
            frame.push(a > b)

        elif op == Opcode.COMPARE_GE:
            b = frame.pop()
            a = frame.pop()
            frame.push(a >= b)

        elif op == Opcode.UNARY_NOT:
            a = frame.pop()
            frame.push(not is_truthy(a))

        elif op == Opcode.UNARY_NEG:
            a = frame.pop()
            frame.push(-a)

        # ---------------------------------------------------------------------
        # Jumps
        # ---------------------------------------------------------------------
        elif op == Opcode.JUMP:
            frame.ip = arg

        elif op == Opcode.JUMP_IF_FALSE:
            cond = frame.pop()
            if not is_truthy(cond):
                frame.ip = arg

        # ---------------------------------------------------------------------
        # Function Calls & Return
        # ---------------------------------------------------------------------
        elif op == Opcode.CALL:
            arg_count = arg
            args: List[Any] = []
            for _ in range(arg_count):
                args.append(frame.pop())
            args.reverse()

            callee = frame.pop()

            if hasattr(callee, "call"):
                # HakaiCallable or HakaiBuiltinFunction
                ret = callee.call(None, args)
                frame.push(ret)
            elif isinstance(callee, HakaiCodeObject):
                # User-defined bytecode function
                new_frame = Frame(callee, frame.globals)
                for idx, p_name in enumerate(callee.param_names):
                    if idx < len(args):
                        new_frame.locals[p_name] = args[idx]
                self.call_stack.push(new_frame)
            elif callable(callee):
                ret = callee(*args)
                frame.push(ret)
            else:
                raise HakaiTypeError(f"VM Call target '{callee}' is not callable.")

        elif op == Opcode.RETURN:
            ret_val = frame.pop()
            self.call_stack.pop()
            if not self.call_stack.is_empty():
                self.call_stack.current().push(ret_val)
            else:
                self.vm.last_result = ret_val
                return False

        elif op == Opcode.POP:
            if frame.stack:
                frame.pop()

        # ---------------------------------------------------------------------
        # Collections & Attributes
        # ---------------------------------------------------------------------
        elif op == Opcode.BUILD_ARRAY:
            count = arg
            elements = [frame.pop() for _ in range(count)]
            elements.reverse()
            frame.push(elements)

        elif op == Opcode.IMPORT_MODULE:
            mod_name = frame.code.names[arg]
            mod_dict = self.vm.runtime_context.load_module(mod_name)
            from interpreter.interpreter import HakaiModuleObject
            frame.push(HakaiModuleObject(mod_name, mod_dict))

        elif op == Opcode.BUILD_CLASS:
            class_data = frame.code.constants[arg]
            sc = None
            if class_data.get("superclass"):
                sc_name = class_data["superclass"]
                sc = frame.globals.get(sc_name) or frame.locals.get(sc_name)
            from interpreter.classes import HakaiClass
            klass = HakaiClass(
                name=class_data["name"],
                superclass=sc,
                methods=class_data["methods"],
                static_methods=class_data["static_methods"],
            )
            frame.push(klass)

        elif op == Opcode.BUILD_MAP:
            count = arg
            m = {}
            for _ in range(count):
                val = frame.pop()
                key = frame.pop()
                m[key] = val
            frame.push(m)

        elif op == Opcode.GET_INDEX:
            idx = frame.pop()
            target = frame.pop()
            if isinstance(target, (list, tuple, str)):
                if idx < -len(target) or idx >= len(target):
                    raise HakaiIndexError(f"Index out of range: {idx}")
                frame.push(target[idx])
            elif isinstance(target, dict):
                frame.push(target[idx])
            else:
                raise HakaiTypeError(f"Cannot index into {hakai_type_name(target)}.")

        elif op == Opcode.SET_INDEX:
            val = frame.pop()
            idx = frame.pop()
            target = frame.pop()
            target[idx] = val
            frame.push(val)

        elif op == Opcode.GET_ATTR:
            name = frame.code.names[arg]
            obj = frame.pop()
            if isinstance(obj, dict) and name in obj:
                frame.push(obj[name])
            elif hasattr(obj, name):
                frame.push(getattr(obj, name))
            else:
                raise HakaiRuntimeError(f"Cannot get attribute '{name}' on {obj}.")

        elif op == Opcode.SET_ATTR:
            name = frame.code.names[arg]
            val = frame.pop()
            obj = frame.pop()
            if isinstance(obj, dict):
                obj[name] = val
            else:
                setattr(obj, name, val)
            frame.push(val)

        elif op == Opcode.HALT:
            return False

        return True
