# -*- coding: utf-8 -*-

import os, sys
import shutil

sys.path.append(os.getcwd())

from typing import List
from JackCompiler import CompilationEngine

def copy_os_vms(path: str):

    assert os.path.exists(path)

    os_vms_dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "OS")
    assert os.path.isdir(os_vms_dir_path)

    if not os.path.isdir(path):
        path = os.path.dirname(os.path.realpath(path))
    print(f"copy OS vm files to: {path}")

    for os_vm_file in os.listdir(os_vms_dir_path):
        if os_vm_file.endswith(".vm"):
            shutil.copyfile(os.path.join(os_vms_dir_path, os_vm_file), os.path.join(path, os_vm_file))
            print(f"    copied OS vm file: {os.path.join(path, os_vm_file)}")


def compile(path: str):

    assert os.path.exists(path)

    jack_files: List[str] = []
    vm_files: List[str] = []

    if os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".jack"):
                jack_files.append(os.path.join(path, file))
                vm_files.append(os.path.join(path, file.replace(".jack", ".vm")))
    else:
        assert path.endswith(".jack")
        jack_files.append(path)
        vm_files.append(path.replace(".jack", ".vm"))

    if len(jack_files) < 1:
        print(f"no jack files in: {path}")
        raise IOError()

    for i in range(len(jack_files)):
        print("jack file to compile: ")
        print(f"  {jack_files[i]}")
        print("vm out file: ")
        print(f"  {vm_files[i]}")

        engine = CompilationEngine(jack_files[i], vm_files[i])
        engine.compile()
        # engine.write()

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

    os_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "OS")
    os_path = os.path.abspath(os_path)
    if path != os_path:
        copy_os_vms(path)
        
    compile(path)
