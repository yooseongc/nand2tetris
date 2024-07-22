# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Union
from . import JackTokenizer
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


class StringConstant:
    def __init__(self, value: str) -> None:
        self.value = value

    def toXMLElements(self) -> List[ET.Element]:
        return [strConstElement(self.value)]

class KeywordConstant:
    def __init__(self, value: str) -> None:
        self.value = value

    def toXMLElements(self) -> List[ET.Element]:
        return [keywordElement(self.value)]

class VarNameTerm:
    def __init__(self, value: str) -> None:
        self.value = value

    def toXMLElements(self) -> List[ET.Element]:
        return [identifierElement(self.value)]


class VarNameWithArrayRefTerm:

    def __init__(self, varNameTerm: VarNameTerm, expression: Expression) -> None:
        self.varNameTerm = varNameTerm
        self.expression = expression

    def toXMLElements(self) -> List[ET.Element]:
        return [self.varNameTerm.toXMLElement(), symbolElement("["), self.expression.toXMLElement(), symbolElement("]")]

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

class ParenthesisTerm:
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def toXMLElements(self) -> List[ET.Element]:
        return [symbolElement("["), self.expression.toXMLElement(), symbolElement("]")]

class UnaryOpTerm:

    def __init__(self, unaryOp: str, term: Term) -> None:
        self.unaryOp = unaryOp
        self.term = term

    def toXMLElements(self) -> List[ET.Element]:
        return [keywordElement(self.unaryOp), self.term.toXMLElement()]

class Term:
    def __init__(self, term: Union[IntegerConstant, StringConstant, KeywordConstant, VarNameTerm, VarNameWithArrayRefTerm, SubroutineCall, ParenthesisTerm, UnaryOpTerm]) -> None:
        self.term = term

    def toXMLElement(self) -> ET.Element:
        root = element("term")
        for elem in self.term.toXMLElements():
            root.append(elem)
        return root

class AdditionalTerm:
    def __init__(
        self,
        op: str,
        term: Term,
    ) -> None:
        self.op = op
        self.term = term

    def toXMLElements(self) -> List[ET.Element]:
        return [symbolElement(self.op), self.term.toXMLElement()]

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

class IfStatement:
    def __init__(self, expression: Expression, statements: Statements, elseStatements: Statements = None) -> None:
        self.expression = expression
        self.statements = statements
        self.elseStataements = elseStatements

    def toXMLElement(self) -> ET.Element:
        root = element("ifStatement")
        root.append(keywordElement("if"))
        root.append(symbolElement("("))
        root.append(self.expression.toXMLElement())
        root.append(symbolElement(")"))
        root.append(symbolElement("{"))
        root.append(self.statements.toXMLElement())
        root.append(symbolElement("}"))
        if self.elseStataements is not None:
            root.append(keywordElement("else"))
            root.append(symbolElement("{"))
            root.append(self.elseStataements.toXMLElement())
            root.append(symbolElement("}"))
        return root

class WhileStatement:
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

class Statements:
    def __init__(self, statements: List[Union[LetStatement, IfStatement, WhileStatement, DoStatement, ReturnStatement]]) -> None:
        self.statements = statements

    def toXMLElement(self) -> ET.Element:
        root = element("statements")
        for statement in self.statements:
            root.append(statement.toXMLElement())
        return root

class ClassVarDec:
    def __init__(self, keyword: str, type: str, identifiers: List[str]) -> None:
        self.keyword = keyword
        self.type = type
        self.identifiers = []

    def toXMLElement(self) -> ET.Element:
        root = element("classVarDec")
        root.append(keywordElement(self.keyword))
        if self.type in ["int", "char", "boolean"]:
            root.append(keywordElement(self.type))
        else:
            root.append(identifierElement(self.type))
        root.append(identifierElement(self.type))
        for idx, identifier in enumerate(self.identifiers):
            if idx != 0:
                root.append(symbolElement(","))
            root.append(identifierElement(identifier))
        root.append(symbolElement(";"))
        return root

class Parameter:
    def __init__(self, type: str, identifier: str) -> None:
        self.type = type
        self.identifier = identifier

    def toXMLElements(self) -> List[ET.Element]:
        return [
            keywordElement(self.type) if self.type in ["int", "char", "boolean"] else identifierElement(self.type), 
            identifierElement(self.identifier)
        ]

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
        root.append(identifierElement(self.type))
        for idx, identifier in enumerate(self.identifiers):
            if idx != 0:
                root.append(symbolElement(","))
            root.append(identifierElement(identifier))
        root.append(symbolElement(";"))
        return root

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

class SubroutineDec:
    def __init__(
        self,
        keyword: str,
        type: str,
        identifier: str,
        parameterList: ParameterList,
        subroutineBody: SubroutineBody,
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
        root.append(self.parameterList.toXMLElement())
        root.append(self.subroutineBody.toXMLElement())
        return root

class Class:
    def __init__(self, identifier: str, classVarDecs: List[ClassVarDec], subroutineDecs: List[SubroutineDec]) -> None:
        self.keyword = "class"
        self.identifier = identifier
        self.classVarDecs = classVarDecs
        self.subroutineDecs = subroutineDecs

    def toXMLElement(self) -> ET:
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

class CompilationEngine:

    def __init__(self, jack_file: str, xml_file: str) -> None:
        self.jack_file = jack_file
        self.xml_file = xml_file
        self.tokenizer = JackTokenizer(jack_file)
        self.tree = ET.ElementTree("classes")
        ET.indent(self.tree, space="  ")

    def compileClass(self) -> Class:
        # 'class' className '{' classVarDec* subroutineDec* '}'
        assert self.tokenizer.tokenType() == "class"
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
        if self.type in ["int", "char", "boolean"]:
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
            assert self.tokenizer.keyword() == "void"
            type = "void"
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
        assert self.tokenizer.symbol() == '('

        parameters = []
        self.tokenizer.advance()
        type = self.tokenizer.keyword()
        self.tokenizer.advance()
        varName = self.tokenizer.identifier()
        parameters.append(Parameter(type, varName))

        self.tokenizer.advance()
        while (self.tokenizer.isSymbol() and self.tokenizer.symbol() == ','):
            type = self.tokenizer.keyword()
            self.tokenizer.advance()
            varName = self.tokenizer.identifier()
            parameters.append(Parameter(type, varName))
            self.tokenizer.advance()

        return ParameterList(parameters)

    def compileVarDec(self) -> ClassVarDec:
        assert self.tokenizer.keyword() == "var"
        self.tokenizer.advance()
        if self.type in ["int", "char", "boolean"]:
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
        while (not (self.tokenizer.isSymbol() and self.tokenizer.symbol == '}')):
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
            self.tokenizer.advance()
        return Statements(sts)

    def compileLet(self) -> LetStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "let"
        self.tokenizer.advance()
        varName = self.tokenizer.identifier()
        self.tokenizer.advance()
        arrayRefExpression = None
        if self.tokenizer.isSymbol() and self.tokenizer.symbol() == '=':
            expression = self.compileExpression()
            self.tokenizer.advance()
        else:
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "["
            self.tokenizer.advance()
            arrayRefExpression = self.compileExpression()
            self.tokenizer.advance()
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "]"
            self.tokenizer.advance()
            expression = self.compileExpression()
            self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"
        self.tokenizer.advance()
        return LetStatement(varName, expression, arrayRefExpression)

    def compileIf(self) -> IfStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "if"
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "("
        self.tokenizer.advance()
        expression = self.compileExpression()
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ")"
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "{"
        self.tokenizer.advance()
        statements = self.compileStatements()
        self.tokenizer.advance()
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "}"
        self.tokenizer.advance()

        elseStatements = None
        if self.tokenizer.isKeyword() and self.tokenizer.keyword() == 'else':
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "{"
            self.tokenizer.advance()
            elseStatements = self.compileStatements()
            self.tokenizer.advance()
            assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == "}"
            self.tokenizer.advance()

        return IfStatement(expression, statements, elseStatements)

    def compileWhile(self) -> WhileStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "while"
        self.tokenizer.advance()
        # TODO
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"
        return WhileStatement()

    def compileDo(self) -> DoStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "do"
        self.tokenizer.advance()
        # TODO
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"
        return DoStatement()

    def compileReturn(self) -> ReturnStatement:
        assert self.tokenizer.isKeyword() and self.tokenizer.keyword() == "return"
        self.tokenizer.advance()
        # TODO
        assert self.tokenizer.isSymbol() and self.tokenizer.symbol() == ";"
        return ReturnStatement()

    def compileExpression(self) -> Expression:
        # TODO
        pass

    def compileTerm(self) -> Term:
        # TODO
        pass

    def compileExpressionList(self) -> ExpressionList:
        # TODO
        pass

    def compile(self) -> None:
        while self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            if self.tokenizer.tokenType() == "class":
                self.tree.getroot().append(self.compileClass().toXMLElement())

    def write(self) -> None:
        self.tree.write(self.xml_file)
