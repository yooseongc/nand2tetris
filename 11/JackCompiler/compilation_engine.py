# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Union
from .tokenizer import JackTokenizer
from .symbol_table import SymbolTable, SymbolKind
from .vm_writer import VMWriter, Segment, ArithmeticCommand
from xml.etree import ElementTree as ET

def element(key: str, text: str = None) -> ET.Element:
    ret = ET.Element(key)
    if text is not None:
        ret.text = f" {text} "
    return ret

def keywordElement(text: str) -> ET.Element:
    return element("keyword", text)

def symbolElement(text: str) -> ET.Element:
    return element("symbol", text)

def identifierElement(text: str) -> ET.Element:
    return element("identifier", text)

def intConstElement(text: str) -> ET.Element:
    return element("integerConstant", text)

def strConstElement(text: str) -> ET.Element:
    return element("stringConstant", text)


class IntegerConstant:
    def __init__(self, value: str) -> None:
        self.value = value

    def toXMLElements(self) -> List[ET.Element]:
        return [intConstElement(self.value)]
    
    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        writer.writePush(Segment.CONST, self.value)

class StringConstant:
    def __init__(self, value: str) -> None:
        self.value = value

    def toXMLElements(self) -> List[ET.Element]:
        return [strConstElement(self.value)]

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        writer.writePush(Segment.CONST, len(self.value))
        writer.writeCall("String.new", 1)
        for c in self.value:
            writer.writePush(Segment.CONST, ord(c))
            writer.writeCall("String.appendChar", 2)

class KeywordConstant:
    def __init__(self, value: str) -> None:
        self.value = value

    def toXMLElements(self) -> List[ET.Element]:
        return [keywordElement(self.value)]

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        if self.value == "false":
            writer.writePush(Segment.CONST, 0)
        elif self.value == "true":
            writer.writePush(Segment.CONST, 0)
            writer.writeArithmetic(ArithmeticCommand.NOT)
        elif self.value == "this":
            writer.writePush(Segment.POINTER, 0)
        elif self.value == "null":
            writer.writePush(Segment.CONST, 0) 

class VarNameTerm:
    def __init__(self, value: str) -> None:
        self.value = value

    def toXMLElements(self) -> List[ET.Element]:
        return [identifierElement(self.value)]

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        if st.kindOf(self.value) == SymbolKind.VAR:
            writer.writePush(Segment.LOCAL, st.indexOf(self.value))
        elif st.kindOf(self.value) == SymbolKind.ARGUMENT:
            writer.writePush(Segment.ARGUMENT, st.indexOf(self.value))
        elif st.kindOf(self.value) == SymbolKind.FIELD:
            writer.writePush(Segment.THIS, st.indexOf(self.value))
        elif st.kindOf(self.value) == SymbolKind.STATIC:
            writer.writePush(Segment.STATIC, st.indexOf(self.value))

class VarNameWithArrayRefTerm:

    def __init__(self, varNameTerm: VarNameTerm, expression: Expression) -> None:
        self.varNameTerm = varNameTerm
        self.expression = expression

    def toXMLElements(self) -> List[ET.Element]:
        return [*self.varNameTerm.toXMLElements(), symbolElement("["), self.expression.toXMLElement(), symbolElement("]")]

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        self.varNameTerm.writeVMCodes(st, writer)
        self.expression.writeVMCodes(st, writer)
        writer.writeArithmetic(ArithmeticCommand.ADD)
        writer.writePop(Segment.POINTER, 1)
        writer.writePush(Segment.THAT, 0)

class SubroutineCall:
    def __init__(self, subroutineName: str, expressionList: ExpressionList, classOrVarName: str = None) -> None:
        self.subroutineName = subroutineName
        self.expressionList = expressionList
        self.classOrVarName = classOrVarName

    def toXMLElements(self) -> List[ET.Element]:
        ret = []
        if self.classOrVarName is not None:
            ret.append(identifierElement(self.classOrVarName))
            ret.append(symbolElement("."))
        ret.append(identifierElement(self.subroutineName))
        ret.append(symbolElement('('))
        ret.append(self.expressionList.toXMLElement())
        ret.append(symbolElement(")"))
        return ret

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:

        if self.classOrVarName is None:
            writer.writePush(Segment.POINTER, 0)
            self.expressionList.writeVMCodes(st, writer)
            writer.writeCall(
                f"{st.className()}.{self.subroutineName}",
                self.expressionList.length() + 1,  # include THIS
            )
        else:
            if st.kindOf(self.classOrVarName) != SymbolKind.NONE:
                if st.kindOf(self.classOrVarName) == SymbolKind.VAR:
                    writer.writePush(Segment.LOCAL, st.indexOf(self.classOrVarName))
                elif st.kindOf(self.classOrVarName) == SymbolKind.ARGUMENT:
                    writer.writePush(Segment.ARGUMENT, st.indexOf(self.classOrVarName))
                elif st.kindOf(self.classOrVarName) == SymbolKind.FIELD:
                    writer.writePush(Segment.THIS, st.indexOf(self.classOrVarName))
                elif st.kindOf(self.classOrVarName) == SymbolKind.STATIC:
                    writer.writePush(Segment.STATIC, st.indexOf(self.classOrVarName))
                self.expressionList.writeVMCodes(st, writer)
                writer.writeCall(
                    f"{st.typeOf(self.classOrVarName)}.{self.subroutineName}",
                    self.expressionList.length() + 1,  # include THIS
                )
            else:
                self.expressionList.writeVMCodes(st, writer)
                writer.writeCall(
                    f"{self.classOrVarName}.{self.subroutineName}",
                    self.expressionList.length(),
                )

class ParenthesisTerm:
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def toXMLElements(self) -> List[ET.Element]:
        return [symbolElement("("), self.expression.toXMLElement(), symbolElement(")")]
    
    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        self.expression.writeVMCodes(st, writer)

class UnaryOpTerm:
    def __init__(self, unaryOp: UnaryOperator, term: Term) -> None:
        self.unaryOp = unaryOp
        self.term = term

    def toXMLElements(self) -> List[ET.Element]:
        return [self.unaryOp.toXMLElement(), self.term.toXMLElement()]

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        self.term.writeVMCodes(st, writer)
        self.unaryOp.writeVMCodes(st, writer)

class Term:
    def __init__(self, term: Union[IntegerConstant, StringConstant, KeywordConstant, VarNameTerm, VarNameWithArrayRefTerm, SubroutineCall, ParenthesisTerm, UnaryOpTerm]) -> None:
        self.term = term

    def toXMLElement(self) -> ET.Element:
        root = element("term")
        for elem in self.term.toXMLElements():
            root.append(elem)
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        self.term.writeVMCodes(st, writer)

class UnaryOperator:
    def __init__(self, op: str) -> None:
        self.op = op

    def toXMLElement(self) -> ET.Element:
        return symbolElement(self.op)

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        if self.op == "~":
            writer.writeArithmetic(ArithmeticCommand.NOT)
        elif self.op == "-":
            writer.writeArithmetic(ArithmeticCommand.NEG)

class Operator:
    def __init__(self, op: str) -> None:
        self.op = op
    
    def toXMLElement(self) -> ET.Element:
        return symbolElement(self.op)
    
    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        if self.op == "+":
            writer.writeArithmetic(ArithmeticCommand.ADD)
        elif self.op == "-":
            writer.writeArithmetic(ArithmeticCommand.SUB)
        elif self.op == "*":
            writer.writeCall("Math.multiply", 2)
        elif self.op == "/":
            writer.writeCall("Math.divide", 2)
        elif self.op == "&":
            writer.writeArithmetic(ArithmeticCommand.AND)
        elif self.op == "|":
            writer.writeArithmetic(ArithmeticCommand.OR)
        elif self.op == "<":
            writer.writeArithmetic(ArithmeticCommand.LT)
        elif self.op == ">":
            writer.writeArithmetic(ArithmeticCommand.GT)
        elif self.op == "=":
            writer.writeArithmetic(ArithmeticCommand.EQ)

class AdditionalTerm:
    def __init__(
        self,
        op: Operator,
        term: Term,
    ) -> None:
        self.op = op
        self.term = term

    def toXMLElements(self) -> List[ET.Element]:
        return [self.op.toXMLElement(), self.term.toXMLElement()]
    
    def writeVMCodes(self, st: SymbolTable, writer: VMWriter, cond: bool = False) -> None:
        self.term.writeVMCodes(st, writer)
        self.op.writeVMCodes(st, writer)

class Expression:
    def __init__(self, term: Term, terms: List[AdditionalTerm]) -> None:
        self.term = term
        self.terms = terms

    def toXMLElement(self) -> ET.Element:
        root = element("expression")
        root.append(self.term.toXMLElement())
        for term in self.terms:
            for elem in term.toXMLElements():
                root.append(elem)
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        self.term.writeVMCodes(st, writer)
        for term in self.terms:
            term.writeVMCodes(st, writer)

class ExpressionList:
    def __init__(self, expressions: List[Expression]) -> None:
        self.expressions = expressions

    def toXMLElement(self) -> ET.Element:
        root = element("expressionList")
        for idx, expression in enumerate(self.expressions):
            if idx > 0:
                root.append(symbolElement(","))
            root.append(expression.toXMLElement())
        return root
    
    def length(self) -> int:
        return len(self.expressions)
    
    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        for expression in self.expressions:
            expression.writeVMCodes(st, writer)

class LetStatement:
    def __init__(self, varName: str, expression: Expression, arrayRefExpression: Expression = None) -> None:
        self.varName = varName
        self.expression = expression
        self.arrayRefExpression = arrayRefExpression

    def toXMLElement(self) -> ET.Element:
        root = element("letStatement")
        root.append(keywordElement("let"))
        root.append(identifierElement(self.varName))
        if self.arrayRefExpression is not None:
            root.append(symbolElement("["))
            root.append(self.arrayRefExpression.toXMLElement())
            root.append(symbolElement("]"))
        root.append(symbolElement("="))
        root.append(self.expression.toXMLElement())
        root.append(symbolElement(";"))
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:

        self.expression.writeVMCodes(st, writer)

        if self.arrayRefExpression is not None:

            if st.kindOf(self.varName) == SymbolKind.VAR:
                writer.writePush(Segment.LOCAL, st.indexOf(self.varName))
            elif st.kindOf(self.varName) == SymbolKind.ARGUMENT:
                writer.writePush(Segment.ARGUMENT, st.indexOf(self.varName))
            elif st.kindOf(self.varName) == SymbolKind.FIELD:
                writer.writePush(Segment.THIS, st.indexOf(self.varName))
            elif st.kindOf(self.varName) == SymbolKind.STATIC:
                writer.writePush(Segment.STATIC, st.indexOf(self.varName))
            else:
                assert True

            self.arrayRefExpression.writeVMCodes(st, writer)
            writer.writeArithmetic(ArithmeticCommand.ADD)
            writer.writePop(Segment.POINTER, 1)
            writer.writePop(Segment.THAT, 0)
            
        else:
            if st.kindOf(self.varName) == SymbolKind.VAR:
                writer.writePop(Segment.LOCAL, st.indexOf(self.varName))
            elif st.kindOf(self.varName) == SymbolKind.ARGUMENT:
                writer.writePop(Segment.ARGUMENT, st.indexOf(self.varName))
            elif st.kindOf(self.varName) == SymbolKind.FIELD:
                writer.writePop(Segment.THIS, st.indexOf(self.varName))
            elif st.kindOf(self.varName) == SymbolKind.STATIC:
                writer.writePop(Segment.STATIC, st.indexOf(self.varName))
            else:
                assert True

class IfStatement:

    LABEL_INDEX = 0

    def __init__(self, expression: Expression, statements: Statements, elseStatements: Statements = None) -> None:
        self.expression: Expression = expression
        self.statements: Statements = statements
        self.elseStatements: Statements = elseStatements

    def toXMLElement(self) -> ET.Element:
        root = element("ifStatement")
        root.append(keywordElement("if"))
        root.append(symbolElement("("))
        root.append(self.expression.toXMLElement())
        root.append(symbolElement(")"))
        root.append(symbolElement("{"))
        root.append(self.statements.toXMLElement())
        root.append(symbolElement("}"))
        if self.elseStatements is not None:
            root.append(keywordElement("else"))
            root.append(symbolElement("{"))
            root.append(self.elseStatements.toXMLElement())
            root.append(symbolElement("}"))
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        label1 = f"{st.className()}.{st.subroutineName()}.IF.{IfStatement.LABEL_INDEX}"
        IfStatement.LABEL_INDEX += 1
        label2 = f"{st.className()}.{st.subroutineName()}.IF.{IfStatement.LABEL_INDEX}"
        IfStatement.LABEL_INDEX += 1

        self.expression.writeVMCodes(st, writer)
        writer.writeArithmetic(ArithmeticCommand.NOT)
        writer.writeIf(label1)
        self.statements.writeVMCodes(st, writer)
        writer.writeGoto(label2)
        writer.writeLabel(label1)
        if self.elseStatements is not None:
            self.elseStatements.writeVMCodes(st, writer)
        writer.writeLabel(label2)

class WhileStatement:

    LABEL_INDEX = 0

    def __init__(self, expression: Expression, statements: Statements) -> None:
        self.expression = expression
        self.statements = statements

    def toXMLElement(self) -> ET.Element:
        root = element("whileStatement")
        root.append(keywordElement("while"))
        root.append(symbolElement("("))
        root.append(self.expression.toXMLElement())
        root.append(symbolElement(")"))
        root.append(symbolElement("{"))
        root.append(self.statements.toXMLElement())
        root.append(symbolElement("}"))
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        label1 = (
            f"{st.className()}.{st.subroutineName()}.WHILE.{WhileStatement.LABEL_INDEX}"
        )
        WhileStatement.LABEL_INDEX += 1
        label2 = (
            f"{st.className()}.{st.subroutineName()}.WHILE.{WhileStatement.LABEL_INDEX}"
        )
        WhileStatement.LABEL_INDEX += 1
        writer.writeLabel(label1)
        self.expression.writeVMCodes(st, writer)
        writer.writeArithmetic(ArithmeticCommand.NOT)
        writer.writeIf(label2)
        self.statements.writeVMCodes(st, writer)
        writer.writeGoto(label1)
        writer.writeLabel(label2)

class DoStatement:

    def __init__(self, subroutineCall: SubroutineCall) -> None:
        self.subroutineCall = subroutineCall

    def toXMLElement(self) -> ET.Element:
        root = element("doStatement")
        root.append(keywordElement("do"))
        for elem in self.subroutineCall.toXMLElements():
            root.append(elem)
        root.append(symbolElement(";"))
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        self.subroutineCall.writeVMCodes(st, writer)
        writer.writePop(Segment.TEMP, 0)


class ReturnStatement:
    def __init__(self, expression: Expression = None) -> None:
        self.expression = expression

    def toXMLElement(self) -> ET.Element:
        root = element("returnStatement")
        root.append(keywordElement("return"))
        if self.expression is not None:
            root.append(self.expression.toXMLElement())
        root.append(symbolElement(";"))
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        if self.expression is None:
            writer.writePush(Segment.CONST, 0)
        else:
            self.expression.writeVMCodes(st, writer)
        writer.writeReturn()

class Statements:
    def __init__(self, statements: List[Union[LetStatement, IfStatement, WhileStatement, DoStatement, ReturnStatement]]) -> None:
        self.statements = statements

    def toXMLElement(self) -> ET.Element:
        root = element("statements")
        for statement in self.statements:
            root.append(statement.toXMLElement())
        return root
    
    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        for statement in self.statements:
            statement.writeVMCodes(st, writer)    

class ClassVarDec:
    def __init__(self, keyword: str, type: str, identifiers: List[str]) -> None:
        self.keyword = keyword
        self.type = type
        self.identifiers = identifiers

    def toXMLElement(self) -> ET.Element:
        root = element("classVarDec")
        root.append(keywordElement(self.keyword))
        if self.type in ["int", "char", "boolean"]:
            root.append(keywordElement(self.type))
        else:
            root.append(identifierElement(self.type))
        for idx, identifier in enumerate(self.identifiers):
            if idx != 0:
                root.append(symbolElement(","))
            root.append(identifierElement(identifier))
        root.append(symbolElement(";"))
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        for varName in self.identifiers:
            st.define(
                varName, self.type, SymbolKind.FIELD if self.keyword == "field" else SymbolKind.STATIC
            )

class Parameter:
    def __init__(self, type: str, identifier: str) -> None:
        self.type = type
        self.identifier = identifier

    def toXMLElements(self) -> List[ET.Element]:
        return [
            keywordElement(self.type) if self.type in ["int", "char", "boolean"] else identifierElement(self.type), 
            identifierElement(self.identifier)
        ]

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        st.define(self.identifier, self.type, SymbolKind.ARGUMENT)

class ParameterList:

    def __init__(self, parameters: List[Parameter]) -> None:
        self.parameters = parameters

    def toXMLElement(self) -> ET.Element:
        root = element("parameterList")
        for idx, parameter in enumerate(self.parameters):
            if idx != 0:
                root.append(symbolElement(","))
            for elem in parameter.toXMLElements():
                root.append(elem)
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        for parameter in self.parameters:
            parameter.writeVMCodes(st, writer)

class VarDec:
    def __init__(self, type: str, identifiers: List[str]) -> None:
        self.keyword = "var"
        self.type = type
        self.identifiers = identifiers

    def toXMLElement(self) -> ET.Element:
        root = element("varDec")
        root.append(keywordElement(self.keyword))
        if self.type in ["int", "char", "boolean"]:
            root.append(keywordElement(self.type))
        else:
            root.append(identifierElement(self.type))
        for idx, identifier in enumerate(self.identifiers):
            if idx != 0:
                root.append(symbolElement(","))
            root.append(identifierElement(identifier))
        root.append(symbolElement(";"))
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        for varName in self.identifiers:
            st.define(varName, self.type, SymbolKind.VAR)

class SubroutineBody:
    def __init__(self, varDecList: List[VarDec], statements: Statements) -> None:
        self.varDecList = varDecList
        self.statements = statements

    def toXMLElement(self) -> ET.Element:
        root = element("subroutineBody")
        root.append(symbolElement("{"))
        for varDec in self.varDecList:
            root.append(varDec.toXMLElement())
        root.append(self.statements.toXMLElement())
        root.append(symbolElement("}"))
        return root

    def getVarDecList(self) -> List[VarDec]:
        return self.varDecList
    
    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        # for varDec in self.varDecList:
        #     varDec.writeVMCodes(st, writer)
        self.statements.writeVMCodes(st, writer)

class SubroutineDec:
    def __init__(
        self,
        keyword: str,
        type: str,
        identifier: str,
        parameterList: ParameterList,
        subroutineBody: SubroutineBody
    ) -> None:
        self.keyword = keyword
        self.type = type
        self.identifier = identifier
        self.parameterList = parameterList
        self.subroutineBody = subroutineBody

    def toXMLElement(self) -> ET.Element:
        root = element("subroutineDec")
        root.append(keywordElement(self.keyword))
        if self.type in ["int", "char", "boolean", "void"]:
            root.append(keywordElement(self.type))
        else:
            root.append(identifierElement(self.type))
        root.append(identifierElement(self.identifier))
        root.append(symbolElement("("))
        root.append(self.parameterList.toXMLElement())
        root.append(symbolElement(")"))
        root.append(self.subroutineBody.toXMLElement())
        return root

    def writeVMCodes(self, st: SymbolTable, writer: VMWriter) -> None:
        st.startSubroutine(self.identifier)
        if self.keyword == "method":
            st.define("this", st.className(), SymbolKind.ARGUMENT)
            
        self.parameterList.writeVMCodes(st, writer)
        
        for varDec in self.subroutineBody.getVarDecList():
            varDec.writeVMCodes(st, writer)

        writer.writeFunction(
            f"{st.className()}.{st.subroutineName()}", st.varCount(SymbolKind.VAR)
        )

        if self.keyword == "method":
            writer.writePush(Segment.ARGUMENT, 0)
            writer.writePop(Segment.POINTER, 0)
        elif self.keyword == "constructor":
            writer.writePush(Segment.CONST, st.varCount(SymbolKind.FIELD))
            writer.writeCall("Memory.alloc", 1)
            writer.writePop(Segment.POINTER, 0)

        self.subroutineBody.writeVMCodes(st, writer)


class Class:
    def __init__(self, identifier: str, classVarDecs: List[ClassVarDec], subroutineDecs: List[SubroutineDec]) -> None:
        self.keyword = "class"
        self.identifier = identifier
        self.classVarDecs = classVarDecs
        self.subroutineDecs = subroutineDecs

    def toXMLElement(self) -> ET.Element:
        root = ET.Element("class")
        root.append(keywordElement(self.keyword))
        root.append(identifierElement(self.identifier))
        root.append(symbolElement("{"))
        for classVarDec in self.classVarDecs:
            root.append(classVarDec.toXMLElement())
        for subroutineDec in self.subroutineDecs:
            root.append(subroutineDec.toXMLElement())
        root.append(symbolElement("}"))
        return root

    def writeVMCodes(self, writer: VMWriter) -> None:
        st = SymbolTable(self.identifier)
        for classVarDec in self.classVarDecs:
            classVarDec.writeVMCodes(st, writer)
        for subroutineDec in self.subroutineDecs:
            subroutineDec.writeVMCodes(st, writer)

class CompilationEngine:

    def __init__(self, jack_file: str, vm_file: str) -> None:
        self.jack_file = jack_file
        self.vm_file = vm_file
        self.tokenizer = JackTokenizer(jack_file)
        self.vm_writer = VMWriter(vm_file)
        self.xml_file = vm_file.replace(".vm", ".xml")
        self.tree = ET.ElementTree(ET.Element("classes"))
        self.tokens = ET.ElementTree(ET.Element("tokens"))

    def compileClass(self) -> Class:
        # 'class' className '{' classVarDec* subroutineDec* '}'
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "class"
        self.tokenizer.advance()
        className = self.tokenizer.identifier()
        self.tokenizer.advance()
        assert self.tokenizer.symbol() == '{'
        self.tokenizer.advance()

        classVarDecs = []
        while (self.tokenizer.isKeyword() and self.tokenizer.keyword() in ["field", "static"]):
            classVarDecs.append(self.compileClassVarDec())

        subroutineDecs = []
        while (self.tokenizer.isKeyword() and self.tokenizer.keyword() in ["constructor", "function", "method"]):
            subroutineDecs.append(self.compileSubroutine())

        assert self.tokenizer.symbol() == "}"
        return Class(className, classVarDecs, subroutineDecs)

    def compileClassVarDec(self) -> ClassVarDec:
        # ('static' | 'field') type varName (',' varName)* ';'
        assert self.tokenizer.keyword() in ["field", "static"]

        sf = self.tokenizer.keyword()
        self.tokenizer.advance()
        if self.tokenizer.isKeyword() and self.tokenizer.keyword() in ["int", "char", "boolean"]:
            type = self.tokenizer.keyword()
        else:
            type = self.tokenizer.identifier()
        self.tokenizer.advance()

        varNames = []
        varNames.append(self.tokenizer.identifier())
        self.tokenizer.advance()
        while (self.tokenizer.isSymbol() and self.tokenizer.symbol() == ','):
            self.tokenizer.advance()
            varNames.append(self.tokenizer.identifier())
            self.tokenizer.advance()

        assert self.tokenizer.symbol() == ';'
        self.tokenizer.advance()
        return ClassVarDec(sf, type, varNames)

    def compileSubroutine(self) -> SubroutineDec:
        # ('constructor' | 'function' | 'method' ) ('void' | type) subroutineName '(' parameterList ')'
        assert self.tokenizer.keyword() in ["constructor", "function", "method"]

        cfm = self.tokenizer.keyword()
        self.tokenizer.advance()

        if self.tokenizer.tokenType() == "keyword":
            assert self.tokenizer.keyword() in ["void", "int", "char", "boolean"]
            type = self.tokenizer.keyword()
        else:
            type = self.tokenizer.identifier()
        self.tokenizer.advance()

        subroutineName = self.tokenizer.identifier()
        self.tokenizer.advance()

        assert self.tokenizer.symbol() == '('
        paramList = self.compileParameterList()
        assert self.tokenizer.symbol() == ')'
        self.tokenizer.advance()

        assert self.tokenizer.symbol() == "{"
        self.tokenizer.advance()

        varDecs = []
        while (self.tokenizer.isKeyword() and self.tokenizer.keyword() == "var"):
            varDecs.append(self.compileVarDec())

        statements = self.compileStatements()
        assert self.tokenizer.symbol() == "}"
        self.tokenizer.advance()

        subroutineBody = SubroutineBody(varDecs, statements)
        return SubroutineDec(cfm, type, subroutineName, paramList, subroutineBody)

    def compileParameterList(self) -> ParameterList:
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == '('
        self.tokenizer.advance()

        parameters: List[Parameter] = []
        if self.tokenizer.isSymbol() and self.tokenizer.symbol() == ')':
            return ParameterList(parameters)

        if self.tokenizer.isKeyword():
            type = self.tokenizer.keyword()
        else:
            type = self.tokenizer.identifier()
        self.tokenizer.advance()
        varName = self.tokenizer.identifier()
        parameters.append(Parameter(type, varName))
        self.tokenizer.advance()

        while (self.tokenizer.isSymbol() and self.tokenizer.symbol() == ','):
            self.tokenizer.advance()
            type = self.tokenizer.keyword()
            self.tokenizer.advance()
            varName = self.tokenizer.identifier()
            parameters.append(Parameter(type, varName))
            self.tokenizer.advance()

        return ParameterList(parameters)

    def compileVarDec(self) -> ClassVarDec:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "var"
        self.tokenizer.advance()

        if self.tokenizer.isKeyword() and self.tokenizer.keyword() in [
            "int",
            "char",
            "boolean",
        ]:
            type = self.tokenizer.keyword()
        else:
            type = self.tokenizer.identifier()
        self.tokenizer.advance()

        varNames = []
        varNames.append(self.tokenizer.identifier())
        self.tokenizer.advance()
        while self.tokenizer.isSymbol() and self.tokenizer.symbol() == ",":
            self.tokenizer.advance()
            varNames.append(self.tokenizer.identifier())
            self.tokenizer.advance()

        assert self.tokenizer.symbol() == ";"
        self.tokenizer.advance()

        return VarDec(type, varNames)

    def compileStatements(self) -> Statements:
        sts = []
        while (not (self.tokenizer.isSymbol() and self.tokenizer.symbol() == '}')):
            if self.tokenizer.keyword() == "let":
                sts.append(self.compileLet())
            elif self.tokenizer.keyword() == "if":
                sts.append(self.compileIf())
            elif self.tokenizer.keyword() == "while":
                sts.append(self.compileWhile())
            elif self.tokenizer.keyword() == "do":
                sts.append(self.compileDo())
            elif self.tokenizer.keyword() == "return":
                sts.append(self.compileReturn())

        return Statements(sts)

    def compileLet(self) -> LetStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "let"
        self.tokenizer.advance()
        varName = self.tokenizer.identifier()
        self.tokenizer.advance()

        arrayRefExpression = None
        if self.tokenizer.isSymbol() and self.tokenizer.symbol() == "[":
            self.tokenizer.advance()
            arrayRefExpression = self.compileExpression()
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "]"
            self.tokenizer.advance()

        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "="
        self.tokenizer.advance()
        expression = self.compileExpression()

        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"
        self.tokenizer.advance()
        return LetStatement(varName, expression, arrayRefExpression)

    def compileIf(self) -> IfStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "if"
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "("
        self.tokenizer.advance()
        expression = self.compileExpression()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ")"
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "{"
        self.tokenizer.advance()
        statements = self.compileStatements()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "}"
        self.tokenizer.advance()

        elseStatements = None
        if self.tokenizer.isKeyword() and self.tokenizer.keyword() == 'else':
            self.tokenizer.advance()
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "{"
            self.tokenizer.advance()
            elseStatements = self.compileStatements()
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "}"
            self.tokenizer.advance()

        return IfStatement(expression, statements, elseStatements)

    def compileWhile(self) -> WhileStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "while"
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "("
        self.tokenizer.advance()
        expression = self.compileExpression()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ")"
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "{"
        self.tokenizer.advance()
        statements = self.compileStatements()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "}"
        self.tokenizer.advance()

        return WhileStatement(expression, statements)

    def compileDo(self) -> DoStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "do"
        self.tokenizer.advance()
        ident1 = self.tokenizer.identifier()
        self.tokenizer.advance()
        ident2 = None
        if (self.tokenizer.isSymbol() and self.tokenizer.symbol() == "."):
            self.tokenizer.advance()
            ident2 = self.tokenizer.identifier()
            self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "("
        self.tokenizer.advance()
        expressionList = self.compileExpressionList()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ")"
        self.tokenizer.advance()

        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"
        self.tokenizer.advance()

        if ident2 is not None:
            return DoStatement(SubroutineCall(ident2, expressionList, ident1))
        else:
            return DoStatement(SubroutineCall(ident1, expressionList))

    def compileReturn(self) -> ReturnStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "return"
        self.tokenizer.advance()
        if (self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"):
            self.tokenizer.advance()
            return ReturnStatement(None)
        expression = self.compileExpression()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"
        self.tokenizer.advance()
        return ReturnStatement(expression)

    def compileExpression(self) -> Expression:
        term = self.compileTerm()
        additionalTerms = []
        while (self.tokenizer.isSymbol() and self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]):
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            aterm = self.compileTerm()
            additionalTerms.append(AdditionalTerm(Operator(op), aterm))

        return Expression(term, additionalTerms)

    def compileTerm(self) -> Term:
        if (self.tokenizer.isIntConst()):
            term = Term(IntegerConstant(self.tokenizer.intVal()))
            self.tokenizer.advance()
        elif (self.tokenizer.isStringConst()):
            term = Term(StringConstant(self.tokenizer.stringVal()))
            self.tokenizer.advance()
        elif (self.tokenizer.isKeyword() and self.tokenizer.keyword() in ['true', 'false', 'null', 'this']):
            term = Term(KeywordConstant(self.tokenizer.keyword()))
            self.tokenizer.advance()
        elif (self.tokenizer.isSymbol() and self.tokenizer.symbol() == '('):
            self.tokenizer.advance()
            term = Term(ParenthesisTerm(self.compileExpression()))
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ")"
            self.tokenizer.advance()
        elif (self.tokenizer.isSymbol() and self.tokenizer.symbol() in ['-', '~']):
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            nestedTerm = self.compileTerm()
            term = Term(UnaryOpTerm(UnaryOperator(op), nestedTerm))
        else:
            ident1 = self.tokenizer.identifier()
            self.tokenizer.advance()
            if (self.tokenizer.isSymbol() and self.tokenizer.symbol() == '['):
                self.tokenizer.advance()
                expression = self.compileExpression()
                assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "]"
                self.tokenizer.advance()
                term = Term(VarNameWithArrayRefTerm(VarNameTerm(ident1), expression))
            elif (self.tokenizer.isSymbol() and self.tokenizer.symbol() == '.'):
                self.tokenizer.advance()
                ident2 = self.tokenizer.identifier()
                self.tokenizer.advance()
                assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "("
                self.tokenizer.advance()
                expressionList = self.compileExpressionList()
                assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ")"
                self.tokenizer.advance()
                term = Term(SubroutineCall(ident2, expressionList, ident1))
            elif (self.tokenizer.isSymbol() and self.tokenizer.symbol() == '('):
                self.tokenizer.advance()
                expressionList = self.compileExpressionList()
                assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ")"
                self.tokenizer.advance()
                term = Term(SubroutineCall(ident1, expressionList))
            else:
                term = Term(VarNameTerm(ident1))

        return term

    def compileExpressionList(self) -> ExpressionList:
        if (self.tokenizer.isSymbol() and self.tokenizer.symbol() == ')'):
            return ExpressionList([])

        expressions = [self.compileExpression()]

        while (self.tokenizer.isSymbol() and self.tokenizer.symbol() == ','):
            self.tokenizer.advance()
            expressions.append(self.compileExpression())

        return ExpressionList(expressions)

    def compile(self) -> None:
        while self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            if self.tokenizer.isKeyword() and self.tokenizer.keyword() == "class":
                clazz = self.compileClass()
                clazz.writeVMCodes(self.vm_writer)
                self.tree.getroot().append(clazz.toXMLElement())
                
        self.vm_writer.close()

    def writeTokens(self) -> None:
        for token in self.tokenizer.getTokens():
            self.tokens.getroot().append(token.toXMLElement())
        ET.indent(self.tokens, space="  ")
        self.tokens.write(self.xml_file.replace(".xml", "T.xml"))

    def writeTree(self) -> None:
        ET.indent(self.tree, space="  ")
        self.tree.write(self.xml_file)

    def write(self) -> None:
        self.writeTree()
        self.writeTokens()

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
