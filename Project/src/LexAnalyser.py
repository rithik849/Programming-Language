import ply.lex as lex
import re

class LexicalAnalyzer():

    keyword = {
        "if" : "IF",
        "else" : "ELSE",
        "while" : "WHILE",
        "for" : "FOR",
        "var" : "VAR",
        "val" : "VAL",
        "print" : "PRINT"
    }

    dataType = {
        "int" : "INT_TYPE",
        "bool" : "BOOL_TYPE",
        "str" : "STRING_TYPE",
        "float" : "FLOAT_TYPE"
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
        "==":"EQUAL" 
    }

    tokens = ("INT","FLOAT","BOOL","STRING","NONE",
            "L_PAR","R_PAR",
            "L_SCOPE","R_SCOPE",
            "COMMA",
            "COL",
            "SEMI_COL",
            "ASSIGNMENT",
            "IDEN",
            "COMMENT"
    )+tuple(keyword.values()+math_op.values()+bool_op.values()+comp_op.values()+dataType.values())

    t_ignore = ' \t\r'

    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno = t.lexer.lineno + len(t.value)

    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def t_COMMENT(self,t):
        r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
        return t

    def t_FLOAT(self,t):
        r'\d+[\.]\d+'
        t.value = float(t.value)
        return t

    def t_INT(self,t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_BOOL(self,t):
        r'True|False'
        t.value = True if t.value=="True" else False
        return t

    def t_STRING(self,t):
        r'\".*\"'
        return t

    def t_NONE(self,t):
        r'None'
        t.value = None
        return t

    def t_L_PAR(self,t):
        r'\('
        return t

    def t_R_PAR(self,t):
        r'\)'
        return t

    def t_L_SCOPE(self,t):
        r'\{'
        return t

    def t_R_SCOPE(self,t):
        r'\}'
        return t

    def t_COMMA(self,t):
        r','
        return t

    def t_COL(self,t):
        r':'
        return t

    def t_SEMI_COL(self,t):
        r';'
        return t

    def t_IDEN(self,t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        reserved = self.keyword.copy()
        reserved.update(self.dataType)
        t.type = reserved.get(t.value,"IDEN")
        return t

    def t_MATH_OP(self,t):
        r'\+|\-|\*|\/|\^|\%'
        t.type = self.math_op.get(t.value)
        return t

    def t_BOOL_OP(self,t):
        r'&&|\|\||!'
        t.type = self.bool_op.get(t.value)
        return t

    def t_COMP_OP(self,t):
        r'<|>|==|!=|>=|<='
        t.type = self.comp_op.get(t.value)
        return t

    def t_ASSIGNMENT(self,t):
        r'='
        return t

    def tokenize(self,data):
        self.lexer.input(data)
        tok = True
        while tok:
            print(tok)
            tok = self.lexer.token()
    
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


m = LexicalAnalyzer()
m.build()
data = ""
with open("testfile.txt","r") as file:
    data = file.read()
m.tokenize(data)