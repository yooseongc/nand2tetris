# -*- coding: utf-8 -*-

import os, sys
sys.path.append(os.getcwd())

from assembler.parser import Parser, CommandType
from assembler.code import dest, comp, jump

def assemble_without_st(path: str):
    parser = Parser(path)
    with open(path.replace(".asm", ".hack"), "w") as f:
        while parser.hasMoreCommands():
            parser.advance()
            if parser.commandType() == CommandType.A_COMMAND:
                symbol = parser.symbol()
                assert symbol.isdigit()
                addr = int(symbol)
                assert addr >= 0 and addr < 2**15
                f.write(f"0{addr:015b}\n")
            elif parser.commandType() == CommandType.C_COMMAND:
                c = comp(parser.comp())
                d = dest(parser.dest())
                j = jump(parser.jump())
                f.write(f"111{c}{d}{j}\n")
            elif parser.commandType() == CommandType.L_COMMAND:
                pass

def assemble_with_st(path: str):
    from assembler.symbol_table import SymbolTable
    symbol_table = SymbolTable()
    parser = Parser(path)
    while parser.hasMoreCommands():
        parser.advance()
        if parser.commandType() == CommandType.L_COMMAND:
            symbol = parser.symbol()
            if not symbol.isdigit():
                symbol_table.addEntry(symbol, parser.index())
    parser.reset()

    with open(path.replace(".asm", ".hack"), "w") as f:
        while parser.hasMoreCommands():
            parser.advance()
            if parser.commandType() == CommandType.A_COMMAND:
                symbol = parser.symbol()
                if symbol.isdigit():
                    addr = int(symbol)
                    assert addr >= 0 and addr < 2**15
                else:
                    symbol_table.addEntry(symbol)
                    addr = symbol_table.getAddress(symbol)
                f.write(f"0{addr:015b}\n")
            elif parser.commandType() == CommandType.C_COMMAND:
                c = comp(parser.comp())
                d = dest(parser.dest())
                j = jump(parser.jump())
                f.write(f"111{c}{d}{j}\n")
    # from pprint import pprint
    # pprint(symbol_table.table)


def assemble(path: str):
    use_symbol = True
    if path.endswith("L.asm"):
        use_symbol = False
    elif not path.endswith(".asm"):
        print("not asm file.")
        raise IOError()

    if use_symbol:
        assemble_with_st(path)
    else:
        assemble_without_st(path)


arguments = sys.argv[1:]
assemble(arguments[0])
