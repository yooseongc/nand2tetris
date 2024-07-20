# -*- coding: utf-8 -*-

from typing import List
from enum import Enum

class Parser:

    class CommandType(Enum):
        C_ARITHMETIC = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        C_PUSH = ["push"]
        C_POP = ["pop"]
        C_LABEL = ["label"]
        C_GOTO = ["goto"]
        C_IF = ["if-goto"]
        C_FUNCTION = ["function"]
        C_RETURN = ["return"]
        C_CALL = ["call"]

    def __init__(self, vm_file: str) -> None:

        self.vm_file = vm_file
        with open(vm_file) as f:
            self.lines = f.readlines()
            assert(len(self.lines) > 0)

        self.line = None
        self.parts = []
        self.line_index = 0

    def getVmFile(self) -> None:
        return self.vm_file 
    
    def hasMoreCommands(self) -> bool:
        return self.line_index < len(self.lines)

    def advance(self) -> None:
        assert(self.hasMoreCommands())
        self.line = self.lines[self.line_index].split("//")[0].strip()
        self.line_index += 1
        while(len(self.line) == 0):
            if not self.hasMoreCommands():
                break
            self.advance()

        if len(self.line) != 0:
            self.parts = self.line.split(" ")

    def commandType(self) -> CommandType:
        for ctype in Parser.CommandType:
            if self.parts[0] in ctype.value:
                return ctype
        assert(True)
        return None

    def arg1(self) -> str:
        assert self._check_has_arg1()
        if self.commandType() == Parser.CommandType.C_ARITHMETIC:
            return self.parts[0]
        else:
            return self.parts[1]

    def arg2(self) -> int:
        assert self._check_has_arg2()
        return self.parts[2]

    def _check_has_arg1(self) -> bool:
        return not self.commandType() == Parser.CommandType.C_RETURN
    
    def _check_has_arg2(self) -> bool:
        return self.commandType() in [
            Parser.CommandType.C_PUSH,
            Parser.CommandType.C_POP,
            Parser.CommandType.C_FUNCTION,
            Parser.CommandType.C_CALL,
        ]
