# -*- coding: utf-8 -*-

from typing import List
from enum import Enum

class Segment(Enum):
    CONST = "constant"
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

    def _write_line(self, code: str) -> None:
        self.f.write(f"{code}\n")

    def _write_lines(self, codes: List[str]) -> None:
        self.f.writelines("\n".join(codes) + "\n")

    def writePush(self, segment: Segment, index: int) -> None:
        self._write_line(f"push {segment.value} {index}")

    def writePop(self, segment: Segment, index: int) -> None:
        self._write_line(f"pop {segment.value} {index}")

    def writeArithmetic(self, command: ArithmeticCommand) -> None:
        self._write_line(command.value)

    def writeLabel(self, label: str) -> None:
        self._write_line(f"label {label}")

    def writeGoto(self, label: str) -> None:
        self._write_line(f"goto {label}")

    def writeIf(self, label: str) -> None:
        self._write_line(f"if-goto {label}")

    def writeCall(self, name: str, nArgs: int) -> None:
        self._write_line(f"call {name} {nArgs}")

    def writeFunction(self, name: str, nLocals: int) -> None:
        self._write_line(f"function {name} {nLocals}")

    def writeReturn(self) -> None:
        self._write_line("return")
