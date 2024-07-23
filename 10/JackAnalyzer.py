# -*- coding: utf-8 -*-

import os, sys

sys.path.append(os.getcwd())

from typing import List
from JackAnalyzer import CompilationEngine

if __name__ == '__main__':
    
    arguments = sys.argv[1:]
    if len(arguments) < 1:
        print("no path in argument")
        sys.exit(1)

    path = arguments[0]
    if not os.path.exists(path):
        print(f"cannot find path: {path}")
        raise IOError()

    path = os.path.abspath(path)

    jack_files: List[str] = []
    xml_files: List[str] = []

    if os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".jack"):
                jack_files.append(os.path.join(path, file))
                xml_files.append(os.path.join(path, file.replace(".jack", ".xml")))
    else:
        assert path.endswith(".jack")
        jack_files.append(path)
        xml_files.append(path.replace(".jack", ".xml"))

    if len(jack_files) < 1:
        print(f"no jack files in: {path}")
        raise IOError()

    for i in range(len(jack_files)):
        print("jack file to tokenize: ")
        print(f"  {jack_files[i]}")
        print("xml out file: ")
        print(f"  {xml_files[i]}")
        print(f"  {xml_files[i].replace('.xml', 'T.xml')}")

        engine = CompilationEngine(jack_files[i], xml_files[i])
        engine.compile()
        engine.write()
