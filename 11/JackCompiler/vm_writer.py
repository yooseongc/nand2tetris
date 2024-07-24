# -*- coding: utf-8 -*-

from typing import List
from enum import Enum

class Segment(Enum):
    CONST = "const"
    ARGUMENT = "argument"
    LOCAL = "local"
    STATIC = "static"
    THIS = "this"
    THAT = "that"
    POINTER = "pointer"
    TEMP = "temp"

class ArithmeticCommand(Enum):
    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"

class VMWriter:

    def __init__(self, vm_file: str) -> None:
        self.vm_file = vm_file
        self.f = open(vm_file, "wt")
    
    def close(self) -> None:
        self.f.close()

    def _write_lines(self, codes: List[str]):
        self.f.writelines("\n".join(codes) + "\n")

    def writePush(self, segment: Segment, index: int) -> None:
        pass

    def writePop(self, segment: Segment, index: int) -> None:
        pass

    def writeArithmetic(self, command: ArithmeticCommand) -> None:
        pass

    def writeLabel(self, label: str) -> None:
        pass

    def writeGoto(self, label: str) -> None:
        pass

    def writeIf(self, label: str) -> None:
        pass

    def writeCall(self, name: str, nArgs: int) -> None:
        pass

    def writeFunction(self, name: str, nLocals: int) -> None:
        pass

    def writeReturn(self) -> None:
        pass
    