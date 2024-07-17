# -*- coding: utf-8 -*-

from enum import Enum

class Parser:

    class CommandType(Enum):
        C_ARITHMETIC = 0
        C_PUSH = 1
        C_POP = 2
        C_LABEL = 3
        C_GOTO = 4
        C_IF = 5
        C_FUNCTION = 6
        C_RETURN = 7
        C_CALL = 8

    def __init__(self, vm_file: str) -> None:

        with open(vm_file) as f:
            self.lines = f.readlines()
            assert(len(self.lines) > 0)

        self.line = None
        self.parts = []
        self.line_index = 0

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
        # TODO
        if self.line in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return Parser.CommandType.C_ARITHMETIC
        elif self.line.startswith("push"):
            return Parser.CommandType.C_PUSH
        elif self.line.startswith("pop"):
            return Parser.CommandType.C_POP
        else:
            assert(True)
            return None

    def arg1(self) -> str:
        assert not self.commandType() == Parser.CommandType.C_RETURN
        if self.commandType() == Parser.CommandType.C_ARITHMETIC:
            return self.parts[0]
        else:
            return self.parts[1]

    def arg2(self) -> int:
        assert self.commandType() in [
            Parser.CommandType.C_PUSH,
            Parser.CommandType.C_POP,
            Parser.CommandType.C_FUNCTION,
            Parser.CommandType.C_CALL
        ]
        return self.parts[2]
