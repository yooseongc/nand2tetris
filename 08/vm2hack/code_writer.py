# -*- coding: utf-8 -*-

import os
from . import Parser
from typing import List


ARITHMETIC_ASSEMBLY_CODES = {
    "add": ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=D+M", "@SP", "M=M+1"],
    "sub": ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M-D", "@SP", "M=M+1"],
    "neg": ["@SP", "AM=M-1", "M=-M", "@SP", "M=M+1"],
    "eq": lambda label_f: (
        not_eq_label := label_f("NOT_EQ"),
        inc_sp_label := label_f("INC_SP"),
    )
    and [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "AM=M-1",
        "D=M-D",
        f"@{not_eq_label}",
        "D;JNE",
        "@SP",
        "A=M",
        "M=-1",
        f"@{inc_sp_label}",
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
    )
    and [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "AM=M-1",
        "D=M-D",
        f"@{not_gt_label}",
        "D;JLE",
        "@SP",
        "A=M",
        "M=-1",
        f"@{inc_sp_label}",
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
    )
    and [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "AM=M-1",
        "D=M-D",
        f"@{not_lt_label}",
        "D;JGE",
        "@SP",
        "A=M",
        "M=-1",
        f"@{inc_sp_label}",
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
    "push_constant": lambda index: [
        f"@{index}",
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "push_local": lambda index: [
        "@LCL",
        "D=M",
        f"@{index}",
        "D=D+A",
        "A=D",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "pop_local": lambda index: [
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "M=D",
        "@LCL",
        "D=M",
        f"@{index}",
        "D=D+A",
        "@R14",
        "M=D",
        "@R13",
        "D=M",
        "@R14",
        "A=M",
        "M=D",
    ],
    "push_argument": lambda index: [
        "@ARG",
        "D=M",
        f"@{index}",
        "D=D+A",
        "A=D",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "pop_argument": lambda index: [
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "M=D",
        "@ARG",
        "D=M",
        f"@{index}",
        "D=D+A",
        "@R14",
        "M=D",
        "@R13",
        "D=M",
        "@R14",
        "A=M",
        "M=D",
    ],
    "push_this": lambda index: [
        "@THIS",
        "D=M",
        f"@{index}",
        "D=D+A",
        "A=D",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "pop_this": lambda index: [
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "M=D",
        "@THIS",
        "D=M",
        f"@{index}",
        "D=D+A",
        "@R14",
        "M=D",
        "@R13",
        "D=M",
        "@R14",
        "A=M",
        "M=D",
    ],
    "push_that": lambda index: [
        "@THAT",
        "D=M",
        f"@{index}",
        "D=D+A",
        "A=D",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "pop_that": lambda index: [
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "M=D",
        "@THAT",
        "D=M",
        f"@{index}",
        "D=D+A",
        "@R14",
        "M=D",
        "@R13",
        "D=M",
        "@R14",
        "A=M",
        "M=D",
    ],
    "push_temp": lambda index: [
        "@R5",
        "D=A",
        f"@{index}",
        "D=D+A",
        "A=D",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "pop_temp": lambda index: [
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "M=D",
        "@R5",
        "D=A",
        f"@{index}",
        "D=D+A",
        "@R14",
        "M=D",
        "@R13",
        "D=M",
        "@R14",
        "A=M",
        "M=D",
    ],
    "push_pointer": lambda index: [
        "@THIS",
        "D=A",
        f"@{index}",
        "D=D+A",
        "A=D",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "pop_pointer": lambda index: [
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "M=D",
        "@THIS",
        "D=A",
        f"@{index}",
        "D=D+A",
        "@R14",
        "M=D",
        "@R13",
        "D=M",
        "@R14",
        "A=M",
        "M=D",
    ],
    "push_static": lambda addr_f, index: [
        f"@{addr_f(index)}",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ],
    "pop_static": lambda addr_f, index: [
        "@SP",
        "AM=M-1",
        "D=M",
        f"@{addr_f(index)}",
        "M=D",
    ],
    "push_segaddr": lambda segment: [
        f"@{segment}",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ],
    "pop_segaddr": lambda segment, to_addr: [
        f"@{to_addr}",
        "D=A",
        "@R13",
        "A=M-D",
        "D=M",
        f"@{segment}",
        "M=D",
    ],
}

class CodeWriter:

    def __init__(self, asm_file: str) -> None:
        self.f = open(asm_file, "w")
        self.name = os.path.basename(asm_file).removesuffix(".asm")
        self.vm_name = self.name
        self.counter = 0

    def writeInit(self) -> None:
        self._write_lines(["@256", "D=A", "@SP", "M=D"])
        self.writeCall("Sys.init", 0)

    def writeArithmetic(self, command: str) -> None:
        if command in ["eq", "gt", "lt"]:
            self._write_lines(ARITHMETIC_ASSEMBLY_CODES[command](self._get_label))
        else:
            self._write_lines(ARITHMETIC_ASSEMBLY_CODES[command])

    def writePushPop(
        self, command: str, segment: str, index: int
    ) -> None:
        if segment == "static":
            self._write_lines(PUSHPOP_ASSEMBLY_CODES[f"{command}_{segment}"](self._get_static_addr, index))
        else:
            self._write_lines(PUSHPOP_ASSEMBLY_CODES[f"{command}_{segment}"](index))

    def writeLabel(self, label: str) -> None:
        self._write_lines([f"({label})"])

    def writeGoto(self, label: str) -> None:
        self._write_lines([f"@{label}", "0;JMP"])

    def writeIf(self, label: str) -> None:
        self._write_lines(["@SP", "AM=M-1", "D=M", f"@{label}", "D;JNE"])

    def writeCall(self, funcName: str, numArgs: int) -> None:
        ret_label = self._get_label(f"FUNC.{funcName}.RETADDR")
        self._write_lines(
            [
                f"@{ret_label}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                *PUSHPOP_ASSEMBLY_CODES["push_segaddr"]("LCL"),
                *PUSHPOP_ASSEMBLY_CODES["push_segaddr"]("ARG"),
                *PUSHPOP_ASSEMBLY_CODES["push_segaddr"]("THIS"),
                *PUSHPOP_ASSEMBLY_CODES["push_segaddr"]("THAT"),
                "@SP",
                "D=M",
                "@5",
                "D=D-A",
                f"@{numArgs}",
                "D=D-A",
                "@ARG",
                "M=D",
                "@SP",
                "D=M",
                "@LCL",
                "M=D",
                f"@{funcName}",
                "0;JMP",
                f"({ret_label})"
            ]
        )

    def writeReturn(self) -> None:
        self._write_lines(
            [
                "@LCL",
                "D=M",
                "@R13",
                "M=D",
                "@5",
                "D=A",
                "@R13",
                "A=M-D",
                "D=M",
                "@R14",
                "M=D",
                "@SP",
                "AM=M-1",
                "D=M",
                "@ARG",
                "A=M",
                "M=D",
                "@ARG",
                "D=M+1",
                "@SP",
                "M=D",
                *PUSHPOP_ASSEMBLY_CODES["pop_segaddr"]("THAT", 1),
                *PUSHPOP_ASSEMBLY_CODES["pop_segaddr"]("THIS", 2),
                *PUSHPOP_ASSEMBLY_CODES["pop_segaddr"]("ARG", 3),
                *PUSHPOP_ASSEMBLY_CODES["pop_segaddr"]("LCL", 4),
                "@R14",
                "A=M",
                "0;JMP"
            ]
        )

    def writeFunction(self, funcName: str, numLocals: int) -> None:
        init_lcls_label = self._get_label(f"FUNC.{funcName}.INITLCLS")
        fin_lcls_label = self._get_label(f"FUNC.{funcName}.FINLCLS")
        self._write_lines(
            [
                f"({funcName})",
                f"@{numLocals}",
                "D=A",
                f"({init_lcls_label})",
                f"@{fin_lcls_label}",
                "D;JEQ",
                "@SP",
                "A=M",
                "M=0",
                "@SP",
                "M=M+1",
                "D=D-1",
                f"@{init_lcls_label}",
                "D;JNE",
                f"({fin_lcls_label})",
            ]
        )

    def close(self) -> None:
        self.f.close()

    def setVmFile(self, filename: str) -> None:
        self.vm_name = os.path.basename(filename).removesuffix(".vm")

    def _get_label(self, prefix: str) -> str:
        self.counter += 1
        return f"{self.name}.{prefix}.{self.counter}"

    def _get_static_addr(self, index: int) -> str:
        return f"{self.vm_name}.{index}"

    def _write_lines(self, codes: List[str]):
        self.f.writelines("\n".join(codes) + "\n")
