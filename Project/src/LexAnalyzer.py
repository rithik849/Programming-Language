
#Library lex taken from ply package
import ply.lex as lex
#Library re taken from python standard library
import re

import SemanticAnalyzer


keyword = {
    "if" : "IF",
    "else" : "ELSE",
    "while" : "WHILE",
    "for" : "FOR",
    "to" : "TO",
    "var" : "VAR",
    "val" : "VAL",
    "print" : "PRINT",
    "def" : "DEF",
    "return" : "RET"
}

dataType = {
    "int" : "INT_TYPE",
    "bool" : "BOOL_TYPE",
    "str" : "STRING_TYPE",
    "float" : "FLOAT_TYPE",
    "none" : "NONE_TYPE"
}

math_op = {
    "+":"ADD",
    "-":"SUB",
    "*":"MUL",
    "/":"DIV",
    "%":"MOD",
    "^":"POW"
}

bool_op = {
    "&&":"AND",
    "||":"OR",
    "!":"NOT"
}

comp_op = {
    "<":"LESS",
    ">":"GREATER",
    "<=":"LESS_EQUAL",
    ">=":"GREATER_EQUAL",
    "==":"EQUAL",
    "!=":"NOT_EQUAL"
}

tokens = ("INT","FLOAT","BOOL","STRING",
        "L_PAR","R_PAR","L_SCOPE","R_SCOPE","L_BRACE","R_BRACE",
        "COMMA",
        "COL",
        "ASSIGNMENT",
        "IDEN",
        "COMMENT"
)+tuple(list(keyword.values())+list(math_op.values())+list(bool_op.values())+list(comp_op.values())+list(dataType.values()))

t_ignore = ' \t\r'

#Record the lines of the file
#Reference : https://ply.readthedocs.io/en/latest/ply.html#line-numbers-and-positional-information
#Accessed : 27-10-2020
def t_newline(t):
    r'\n+'
    t.lexer.lineno = t.lexer.lineno + len(t.value)

#Reset the line numbering when we reach the end of the file
def t_eof(t):
    t.lexer.lineno = 1

def t_error(t):
    SemanticAnalyzer.getErrors().add("Lexical Error Line "+str(t.lexer.lineno)+": Illegal character '"+str(t.value[0])+"'")
    t.lexer.skip(1)

def t_COMMENT(t):
    r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
    t.lexer.lineno += t.value.count("\n")
    pass

def t_FLOAT(t):
    r'\d+[\.]\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_BOOL(t):
    r'True|False'
    t.value = True if t.value=="True" else False
    return t

def t_STRING(t):
    r'["](.*)["]|[\'](.*)[\']'
    return t


def t_L_PAR(t):
    r'\('
    return t

def t_R_PAR(t):
    r'\)'
    return t

def t_L_SCOPE(t):
    r'\{'
    return t

def t_R_SCOPE(t):
    r'\}'
    return t

def t_L_BRACE(t):
    r'\['
    return t

def t_R_BRACE(t):
    r'\]'
    return t

def t_COMMA(t):
    r','
    return t

def t_COL(t):
    r':'
    return t

def t_IDEN(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    reserved = keyword.copy()
    reserved.update(dataType)
    t.type = reserved.get(t.value,"IDEN")
    return t

def t_MATH_OP(t):
    r'\+|\-|\*|\/|\^|\%'
    t.type = math_op.get(t.value)
    return t

def t_COMP_OP(t):
    r'>=|<=|==|!=|<|>'
    t.type = comp_op.get(t.value)
    return t

def t_BOOL_OP(t):
    r'&&|\|\||!'
    t.type = bool_op.get(t.value)
    return t

def t_ASSIGNMENT(t):
    r'='
    return t

lexer = lex.lex(errorlog=lex.NullLogger())

def tokenize_test(string):
    lexer.input(string)
    tokens = []
    #Find next token in lexer and print it out
    tok=lexer.token()
    while tok:
        tokens.append(tok)
        tok = lexer.token()
    return tokens

def tokenize(filename):
    data = ""
    with open(filename,"r") as file:
        data = file.read()
    lexer.input(data)
    tok = lexer.token()
    while tok:
        print(tok)
        tok = lexer.token()