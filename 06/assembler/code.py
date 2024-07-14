# -*- coding: utf-8 -*-

DEST_MNEMONICS = "ADM"
COMP_MNEMONICS_MAP = {
      "0":   "0101010",
      "1":   "0111111",
     "-1":   "0111010",
      "D":   "0001100",
      "A":   "0110000",
     "!D":   "0001101",
     "!A":   "0110001",
     "-D":   "0001111",
     "-A":   "0110011",
    "D+1":   "0011111",
    "A+1":   "0110111",
    "D-1":   "0001110",
    "A-1":   "0110010",
    "D+A":   "0000010",
    "D-A":   "0010011",
    "A-D":   "0000111",
    "D&A":   "0000000",
    "D|A":   "0010101",
      "M":   "1110000",
     "!M":   "1110001",
     "-M":   "1110011",
    "M+1":   "1110111",
    "M-1":   "1110010",
    "D+M":   "1000010",
    "D-M":   "1010011",
    "M-D":   "1000111",
    "D&M":   "1000000",
    "D|M":   "1010101",
}

JMP_MNEMONICS_MAP = {
       "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

def dest(mnemonic: str) -> str:
    bits = ""
    for dest_mnemonic in DEST_MNEMONICS:
        bits += "1" if dest_mnemonic in mnemonic else "0"
    return bits

def comp(mnemonic: str) -> str:
    if mnemonic in  COMP_MNEMONICS_MAP:
        return COMP_MNEMONICS_MAP[mnemonic]
    elif "-" in mnemonic and mnemonic[::-1] in COMP_MNEMONICS_MAP:
        return COMP_MNEMONICS_MAP[mnemonic[::-1]]
    assert False

def jump(mnemonic: str) -> str:
    if mnemonic in JMP_MNEMONICS_MAP:
        return JMP_MNEMONICS_MAP[mnemonic]
    assert False
