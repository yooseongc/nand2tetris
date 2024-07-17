# -*- coding: utf-8 -*-


import os, sys
sys.path.append(os.getcwd())

from typing import List
from vm2hack import Parser, CodeWriter

def translate(vm_files: List[str], asm_file: str) -> None:
    parsers = list(map(lambda vm_file: Parser(vm_file), vm_files))
    code_writer = CodeWriter(asm_file)

    for parser in parsers:
        while(parser.hasMoreCommands()):
            parser.advance()
            print(f"idx: {parser.line_index:05d} line: '{parser.line}'")
            if parser.commandType() == Parser.CommandType.C_ARITHMETIC:
                code_writer.writeArithmetic(parser.arg1())
            else:
                code_writer.writePushPop(parser.commandType(), parser.arg1(), parser.arg2())

    code_writer.close()


def main():
    arguments = sys.argv[1:]
    if len(arguments) < 1:
        print("no path in argument")
        sys.exit(1)

    path = arguments[0]
    if not os.path.exists(path):
        print(f"cannot find path: {path}")
        raise IOError()

    path = os.path.abspath(path)

    vm_files: List[str] = []
    asm_file = None

    if os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".vm"):
                vm_files.append(os.path.join(path, file))
        asm_file = os.path.join(path, os.path.basename(path) + ".asm")
    else:
        vm_files.append(path)
        asm_file = path.replace(".vm", ".asm")

    if len(vm_files) < 1:
        print(f"no vm files in: {path}")
        raise IOError()

    print("vm files to translate: ")
    for vm_file in vm_files:
        print(f"  {vm_file}")

    print("asm out file: ")
    print(f"  {asm_file}")

    translate(vm_files, asm_file)


if __name__ == "__main__":
    main()
