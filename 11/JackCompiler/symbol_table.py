# -*- coding: utf-8 -*-

from typing import List, Dict
from enum import Enum


class SymbolKind(Enum):
    STATIC = "static"
    FIELD = "field"
    ARGUMENT = "argument"
    VAR = "var"
    NONE = "none"

class Symbol:

    def __init__(self, name: str, type: str, kind: SymbolKind, index: int) -> None:
        self.name: str = name
        self.type: str = type
        self.kind: SymbolKind = kind
        self.index: int = index

    def name(self) -> str:
        return self.name

    def type(self) -> str:
        return self.type
    
    def kind(self) -> SymbolKind:
        return self.kind

    def index(self) -> int:
        return self.index

    def __str__(self) -> str:
        return f"Symbol[name={self.name}, type={self.type}, kind={self.kind.value}, index={self.index}]"

    def __repr__(self) -> str:
        return self.__str__()

class SymbolTable:
    
    def __init__(self, class_name: str) -> None:
        self.class_name = class_name
        self.subroutine_name = None
        self.class_table: Dict[str, Symbol] = {}
        self.subroutine_table: Dict[str, Symbol] = {}
        self.static_idx = 0
        self.field_idx = 0
        self.argument_idx = 0
        self.var_idx = 0
    
    def className(self) -> str:
        return self.class_name
    
    def subroutineName(self) -> str:
        return self.subroutine_name
    
    def startSubroutine(self, subroutineName: str) -> None:
        self.subroutine_name = subroutineName
        self.subroutine_table: Dict[str, Symbol] = {}
        self.argument_idx = 0
        self.var_idx = 0

    def define(self, name: str, type: str, kind: SymbolKind) -> None:
        is_class_symbol = True
        if kind == SymbolKind.STATIC:
            idx = self.static_idx
            self.static_idx += 1
        elif kind == SymbolKind.FIELD:
            idx = self.field_idx
            self.field_idx += 1
        elif kind == SymbolKind.ARGUMENT:
            is_class_symbol = False
            idx = self.argument_idx
            self.argument_idx += 1
        elif kind == SymbolKind.VAR:
            is_class_symbol = False
            idx = self.var_idx
            self.var_idx += 1
        else:
            assert True
        
        if is_class_symbol:
            self.class_table[name] = Symbol(name, type, kind, idx)
        else:
            self.subroutine_table[name] = Symbol(name, type, kind, idx)

    def varCount(self, kind: SymbolKind) -> int:
        table = self.class_table if kind in [SymbolKind.STATIC, SymbolKind.FIELD] else self.subroutine_table
        return len([symbol for symbol in table.items() if symbol.kind() == kind])

    def kindOf(self, name: str) -> SymbolKind:
        if self.subroutine_table.get(name) is None:
            if self.class_table.get(name) is None:
                return SymbolKind.NONE
            return self.class_table[name].kind()
        return self.subroutine_table[name].kind()

    def typeOf(self, name: str) -> str:
        if self.subroutine_table.get(name) is None:
            if self.class_table.get(name) is None:
                assert True
            return self.class_table[name].type()
        return self.subroutine_table[name].type()
    
    def indexOf(self, name: str) -> int:
        if self.subroutine_table.get(name) is None:
            if self.class_table.get(name) is None:
                assert True
            return self.class_table[name].index()
        return self.subroutine_table[name].index()
