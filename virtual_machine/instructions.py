"""Bytecode instructions and compiled code object definition for HAKAI VM."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional


class Opcode(IntEnum):
    LOAD_CONST = 1
    LOAD_NAME = 2
    STORE_NAME = 3
    ADD = 4
    SUB = 5
    MUL = 6
    DIV = 7
    MOD = 8
    POW = 9
    COMPARE_EQ = 10
    COMPARE_NE = 11
    COMPARE_LT = 12
    COMPARE_LE = 13
    COMPARE_GT = 14
    COMPARE_GE = 15
    UNARY_NOT = 16
    UNARY_NEG = 17
    JUMP = 18
    JUMP_IF_FALSE = 19
    CALL = 20
    RETURN = 21
    POP = 22
    BUILD_ARRAY = 23
    BUILD_MAP = 24
    GET_INDEX = 25
    SET_INDEX = 26
    GET_ATTR = 27
    SET_ATTR = 28
    HALT = 29
    IMPORT_MODULE = 30
    BUILD_CLASS = 31


@dataclass
class Instruction:
    opcode: Opcode
    operand: Optional[int] = None
    line: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": int(self.opcode),
            "arg": self.operand,
            "line": self.line,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Instruction:
        return cls(
            opcode=Opcode(data["op"]),
            operand=data.get("arg"),
            line=data.get("line", 1),
        )


@dataclass
class HakaiCodeObject:
    """Compiled bytecode unit."""

    name: str
    constants: List[Any]
    names: List[str]
    instructions: List[Instruction]
    param_names: List[str] = field(default_factory=list)
    version: str = "1.0.0"

    MAGIC_HEADER = b"HBC\x01"

    def to_dict(self) -> Dict[str, Any]:
        def _serialize_val(val: Any) -> Any:
            if isinstance(val, HakaiCodeObject):
                return {"__hbc__": True, **val.to_dict()}
            if isinstance(val, dict):
                return {k: _serialize_val(v) for k, v in val.items()}
            if isinstance(val, list):
                return [_serialize_val(x) for x in val]
            return val

        return {
            "name": self.name,
            "version": self.version,
            "constants": [_serialize_val(c) for c in self.constants],
            "names": self.names,
            "param_names": self.param_names,
            "instructions": [ins.to_dict() for ins in self.instructions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HakaiCodeObject:
        def _deserialize_val(val: Any) -> Any:
            if isinstance(val, dict):
                if val.get("__hbc__"):
                    val_copy = dict(val)
                    del val_copy["__hbc__"]
                    return cls.from_dict(val_copy)
                return {k: _deserialize_val(v) for k, v in val.items()}
            if isinstance(val, list):
                return [_deserialize_val(x) for x in val]
            return val

        return cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            constants=[_deserialize_val(c) for c in data["constants"]],
            names=data["names"],
            param_names=data.get("param_names", []),
            instructions=[Instruction.from_dict(i) for i in data["instructions"]],
        )

    def serialize(self) -> bytes:
        payload = json.dumps(self.to_dict()).encode("utf-8")
        return self.MAGIC_HEADER + payload

    @classmethod
    def deserialize(cls, data: bytes) -> HakaiCodeObject:
        if not data.startswith(cls.MAGIC_HEADER):
            raise ValueError("Invalid HAKAI bytecode file format: missing HBC header.")
        payload = data[len(cls.MAGIC_HEADER) :].decode("utf-8")
        parsed = json.loads(payload)
        return cls.from_dict(parsed)
