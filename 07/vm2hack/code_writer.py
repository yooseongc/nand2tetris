# -*- coding: utf-8 -*-

import os
from . import Parser


ARITHMETIC_ASSEMBLY_CODES = {
    "add": ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M+D", "@SP", "M=M+1"],
    "sub": ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M-D", "@SP", "M=M+1"],
    "neg": ["@SP", "AM=M-1", "M=-M", "@SP", "M=M+1"],
    "eq": lambda label_f: (
        not_eq_label := label_f("NOT_EQ"),
        inc_sp_label := label_f("INC_SP"),
    ) and [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "AM=M-1",
        "D=M-D",
        not_eq_label,
        "D;JNE",
        "@SP",
        "A=M",
        "M=-1",
        inc_sp_label,
        "0;JMP",
        f"({not_eq_label})",
        "@SP",
        "A=M",
        "M=0",
        f"({inc_sp_label})",
        "@SP",
        "M=M+1",
    ],
    "gt": lambda label_f: (
        not_gt_label := label_f("NOT_GT"),
        inc_sp_label := label_f("INC_SP"),
    ) and [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "AM=M-1",
        "D=M-D",
        not_gt_label,
        "D;JLE",
        "@SP",
        "A=M",
        "M=-1",
        inc_sp_label,
        "0;JMP",
        f"({not_gt_label})",
        "@SP",
        "A=M",
        "M=0",
        f"({inc_sp_label})",
        "@SP",
        "M=M+1",
    ],
    "lt": lambda label_f: (
        not_lt_label := label_f("NOT_LT"),
        inc_sp_label := label_f("INC_SP"),
    ) and [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "AM=M-1",
        "D=M-D",
        not_lt_label,
        "D;JGE",
        "@SP",
        "A=M",
        "M=-1",
        inc_sp_label,
        "0;JMP",
        f"({not_lt_label})",
        "@SP",
        "A=M",
        "M=0",
        f"({inc_sp_label})",
        "@SP",
        "M=M+1",
    ],
    "and": ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=D&M", "@SP", "M=M+1"],
    "or": ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=D|M", "@SP", "M=M+1"],
    "not": ["@SP", "AM=M-1", "M=!M", "@SP", "M=M+1"],
}

PUSHPOP_ASSEMBLY_CODES = {
    "push_constant": lambda index: [f"@{index}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"],
}

class CodeWriter:

    def __init__(self, asm_file: str) -> None:
        self.f = open(asm_file, "w")
        self.name = os.path.basename(asm_file).removesuffix(".vm")
        self.counter = 0

    def writeArithmetic(self, command: str) -> None:
        if command in ["eq", "gt", "lt"]:
            self.f.writelines(
                "\n".join(ARITHMETIC_ASSEMBLY_CODES[command](self._get_label)) + "\n"
            )
        else:
            self.f.writelines("\n".join(ARITHMETIC_ASSEMBLY_CODES[command]) + "\n")

    def writePushPop(
        self, command: Parser.CommandType, segment: str, index: int
    ) -> None:
        if command == Parser.CommandType.C_PUSH:
            comm = "push"
        else:
            comm = "pop"
        self.f.writelines(
            "\n".join(PUSHPOP_ASSEMBLY_CODES[f"{comm}_{segment}"](index)) + "\n"
        )

    def close(self) -> None:
        self.f.close()

    def _get_label(self, prefix: str) -> str:
        self.counter += 1
        return f"@{self.name}.{prefix}.{self.counter}"
