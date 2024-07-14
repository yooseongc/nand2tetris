# -*- coding: utf-8 -*-

from os.path import exists
from enum import Enum


class CommandType(Enum):
    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2


class Parser:
    def __init__(self, path: str) -> None:

        self.path = path

        if not exists(path):
            raise FileNotFoundError()

        with open(path) as f:
            self.lines = f.readlines()
            self.line_index = 0
            self.line = self.lines[0]
            self.code_line_index = 0

    def hasMoreCommands(self) -> bool:
        return self.line_index < (len(self.lines) - 1) 

    def index(self) -> int:
        return self.code_line_index

    def advance(self) -> None:
        assert self.hasMoreCommands()
        self._get_next_line()
        while len(self.line) == 0:
            self._get_next_line()
            
        if self.commandType() != CommandType.L_COMMAND:
            self.code_line_index += 1

    def commandType(self) -> CommandType:
        if self.line.startswith("@"):
            return CommandType.A_COMMAND
        elif self.line.startswith("(") and self.line.endswith(")"):
            return CommandType.L_COMMAND
        else:
            return CommandType.C_COMMAND

    def symbol(self) -> str:
        assert self.commandType() != CommandType.C_COMMAND
        sb = None
        if self.commandType() == CommandType.L_COMMAND:
            return self.line[1:-1].strip()
        else:
            return self.line[1:]

    def dest(self) -> str:
        assert self.commandType() == CommandType.C_COMMAND
        tokens = self.line.split("=")
        assert len(tokens) > 0 and len(tokens) < 3
        if len(tokens) == 1:  # no '='
            return ""
        else:  # has '='
            return tokens[0]

    def comp(self) -> str:
        assert self.commandType() == CommandType.C_COMMAND
        tokens = self.line.split("=")
        assert len(tokens) > 0 and len(tokens) < 3
        if len(tokens) == 1:  # no '='
            return tokens[0].split(";")[0]
        else: # has '='
            return tokens[1].split(";")[0]

    def jump(self) -> str:
        assert self.commandType() == CommandType.C_COMMAND
        tokens = self.line.split(";")
        assert len(tokens) < 3
        if len(tokens) == 1:
            return ""
        else:
            return tokens[1]

    def reset(self) -> None:
        self.line_index = 0
        self.code_line_index = 0
        self.line = self.lines[0]

    def _get_next_line(self) -> None:
        self.line_index += 1
        self.line = self.lines[self.line_index].split("//")[0].strip()
