# -*- coding: utf-8 -*-


from typing import List
from enum import Enum

class TokenType(Enum):
    KEYWORD = "keyword"
    SYMBOL = "symbol"
    IDENTIFIER = "identifier"
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"


class Token:

    def __init__(self, type: TokenType, value: str) -> None:
        self.type = type
        self.val = value

    @classmethod
    def create(cls, value: str):

        for keyword in Keyword:
            if keyword.value.match(value):
                return keyword.value

        for symbol in Symbol:
            if symbol.value.match(value):
                return symbol.value

        token = Token(TokenType.INT_CONST, value)
        if token.match(value):
            return token

        token = Token(TokenType.STRING_CONST, value)
        if token.match(value):
            return token

        token = Token(TokenType.IDENTIFIER, value)
        if token.match(value):
            return token

        return Token(None, value)

    def tokenType(self) -> TokenType:
        return self.type

    def value(self) -> str:
        if self.isStringConst():
            return self.val[1:-1]
        return self.val

    def isKeyword(self) -> bool:
        return self.type == TokenType.KEYWORD

    def isSymbol(self) -> bool:
        return self.type == TokenType.SYMBOL

    def isIdentifier(self) -> bool:
        return self.type == TokenType.IDENTIFIER

    def isIntConst(self) -> bool:
        return self.type == TokenType.INT_CONST

    def isStringConst(self) -> bool:
        return self.type == TokenType.STRING_CONST

    def match(self, value: str) -> bool:
        if self.type in [TokenType.KEYWORD, TokenType.SYMBOL]:
            return self.val == value
        elif self.type == TokenType.INT_CONST:
            return value.isdigit()
        elif self.type == TokenType.STRING_CONST:
            return (
                value.startswith('"')
                and value.endswith('"')
                and "\n" not in value[1:-1]
                and '"' not in value[1:-1]
            )
        else:
            return not value[0].isdigit() and value.replace("_", "").isalnum()

    def __str__(self) -> str:
        return f"Token(type={self.tokenType()}, value='{self.val}')"

    def __repr__(self) -> str:
        return f"Token(type={self.tokenType()}, value='{self.val}')"

class Keyword(Enum):
    CLASS  = Token(TokenType.KEYWORD, "class")
    METHOD = Token(TokenType.KEYWORD, "method")
    FUNCTION = Token(TokenType.KEYWORD, "function")
    CONSTRUCTOR = Token(TokenType.KEYWORD, "constructor")
    INT = Token(TokenType.KEYWORD, "int")
    BOOLEAN = Token(TokenType.KEYWORD, "boolean")
    CHAR = Token(TokenType.KEYWORD, "char")
    VOID = Token(TokenType.KEYWORD, "void")
    VAR = Token(TokenType.KEYWORD, "var")
    STATIC = Token(TokenType.KEYWORD, "static")
    FIELD = Token(TokenType.KEYWORD, "field")
    LET = Token(TokenType.KEYWORD, "let")
    DO = Token(TokenType.KEYWORD, "do")
    IF = Token(TokenType.KEYWORD, "if")
    ELSE = Token(TokenType.KEYWORD, "void")
    WHILE = Token(TokenType.KEYWORD, "while")
    RETURN = Token(TokenType.KEYWORD, "return")
    TRUE = Token(TokenType.KEYWORD, "true")
    FALSE = Token(TokenType.KEYWORD, "false")
    NULL = Token(TokenType.KEYWORD, "null")
    THIS = Token(TokenType.KEYWORD, "this")

class Symbol(Enum):
    LCB = Token(TokenType.SYMBOL, "{")
    RCB = Token(TokenType.SYMBOL, "}")
    LP = Token(TokenType.SYMBOL, "(")
    RP = Token(TokenType.SYMBOL, ")")
    LB = Token(TokenType.SYMBOL, "[")
    RB = Token(TokenType.SYMBOL, "]")
    DOT = Token(TokenType.SYMBOL, ".")
    COMMA = Token(TokenType.SYMBOL, ",")
    SEMICOLON = Token(TokenType.SYMBOL, ";")
    PLUS = Token(TokenType.SYMBOL, "+")
    MINUS = Token(TokenType.SYMBOL, "-")
    MULT = Token(TokenType.SYMBOL, "*")
    DIV = Token(TokenType.SYMBOL, "/")
    AMP = Token(TokenType.SYMBOL, "&")
    OR = Token(TokenType.SYMBOL, "|")
    LT = Token(TokenType.SYMBOL, "<")
    RT = Token(TokenType.SYMBOL, ">")
    EQ = Token(TokenType.SYMBOL, "=")
    NOT = Token(TokenType.SYMBOL, "~")

class JackTokenizer:

    def __init__(self, jack_file: str) -> None:
        self.jack_file: str = jack_file
        self.tokens: List[Token] = []

        self.stringValIdx = 0
        self.stringVals = {}

        with open(self.jack_file, "rt", newline='\n') as f:
            content: str = f.read()

        comm_start = content.find("/*")
        while(comm_start >= 0):
            comm_end = content[comm_start+2:].find("*/")
            assert comm_end >= 0 and (comm_start + 2 + comm_end) < len(content)
            lfs = content[comm_start+2:comm_end-1].count('\n')
            content = content[0:comm_start] + " " + "\n"*lfs + content[comm_start + 2 + comm_end+2:]
            # print(f"comm_start: {comm_start}, comm_end: {comm_end}")
            comm_start = content.find("/*")
            comm_end = -1

        lines = [line.split("//")[0].strip() for line in content.splitlines()]
        content = "\n".join(lines)

        string_val_start = content.find('"')
        while(string_val_start >= 0):
            string_val_end = content[string_val_start+1:].find('"')
            assert string_val_end >= 0 and (
                string_val_start + 1 + string_val_end
            ) < len(content)
            string_val_token = content[
                string_val_start + 1 : string_val_start + 1 + string_val_end
            ]
            self.stringVals[f"STRINGVAL{self.stringValIdx}"] = string_val_token
            # print(f"STRINGVAL{self.stringValIdx} = '{string_val_token}'")
            content = (
                content[0:string_val_start]
                + f" STRINGVAL{self.stringValIdx} "
                + content[string_val_start + 1 + string_val_end + 1 :]
            )
            self.stringValIdx = self.stringValIdx + 1
            string_val_start = content.find('"')

        for symbol in [s.value.value() for s in Symbol]:
            content = content.replace(symbol, f" {symbol} ")

        for line in content.splitlines():
            if len(line) == 0:
                continue

            curr_tokens = [
                (
                    '"' + self.stringVals[curr_token] + '"'
                    if curr_token in self.stringVals.keys()
                    else curr_token
                )
                for curr_token in line.split()
            ]
            for curr_token in curr_tokens:
                print(f"line: '{' '.join(curr_tokens)}', token: '{curr_token}'")
                self.tokens.append(Token.create(curr_token))

        for token in self.tokens:
            print(token)

        self.token_index: int = 0
        self.token: Token = None

    def hasMoreTokens(self) -> bool:
        return self.token_index < len(self.tokens)

    def advance(self) -> None:
        assert self.hasMoreTokens()
        self.token = self.tokens[self.token_index]
        self.token_index = self.token_index + 1

    def tokenType(self) -> str:
        assert self.token is not None
        return self.token.tokenType().value

    def keyword(self) -> str:
        assert self.token is not None
        assert self.token.isKeyword()
        return self.token.value()

    def symbol(self) -> str:
        assert self.token is not None
        assert self.token.isSymbol()
        return self.token.value()

    def identifier(self) -> str:
        assert self.token is not None
        assert self.token.isIdentifier()
        return self.token.value()

    def intVal(self) -> int:
        assert self.token is not None
        assert self.token.isIntConst()
        return int(self.token.value())

    def stringVal(self) -> str:
        assert self.token is not None
        assert self.token.isStringConst()
        return self.token.value()

    def isKeyword(self) -> bool:
        assert self.token is not None
        return self.token.isKeyword()

    def isSymbol(self) -> bool:
        assert self.token is not None
        return self.token.isSymbol()

    def isIdentifier(self) -> bool:
        assert self.token is not None
        return self.token.isIdentifier()

    def isIntConst(self) -> bool:
        assert self.token is not None
        return self.token.isIntConst()

    def isStringConst(self) -> bool:
        assert self.token is not None
        return self.token.isStringConst()


if __name__ == '__main__':

    import os, sys
    from xml.etree import ElementTree as ET

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
                xml_files.append(os.path.join(path, file.replace(".jack", "T.xml")))
    else:
        assert path.endswith(".jack")
        jack_files.append(path)
        xml_files.append(path.replace(".jack", "T.xml"))

    if len(jack_files) < 1:
        print(f"no jack files in: {path}")
        raise IOError()

    for i in range(len(jack_files)):
        print("jack file to tokenize: ")
        print(f"  {jack_files[i]}")
        print("xml out file: ")
        print(f"  {xml_files[i]}")

        tokenizer = JackTokenizer(jack_files[i])

        tokens = ET.Element("tokens")
        
        while (tokenizer.hasMoreTokens()):
            tokenizer.advance()
            elem = ET.SubElement(tokens, tokenizer.tokenType())
            if tokenizer.tokenType() == TokenType.KEYWORD.value:
                elem.text = " " + tokenizer.keyword() + " "
            elif tokenizer.tokenType() == TokenType.SYMBOL.value:
                elem.text = " " + tokenizer.symbol() + " "
            elif tokenizer.tokenType() == TokenType.IDENTIFIER.value:
                elem.text = " " + tokenizer.identifier() + " "
            elif tokenizer.tokenType() == TokenType.INT_CONST.value:
                elem.text = " " + str(tokenizer.intVal()) + " "
            elif tokenizer.tokenType() == TokenType.STRING_CONST.value:
                elem.text = " " + tokenizer.stringVal() + " "

        tree = ET.ElementTree(tokens)
        ET.indent(tree, space="")
        tree.write(xml_files[i])
