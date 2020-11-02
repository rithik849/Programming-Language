from SemanticAnalyzer import *

class AST:

    self.tree = object()
    self.i = 0
    self.errors = []

    def __init__(self,token_stream):
        self.token_stream = token_stream
        self.parse(self.token_stream)

    def parse_var(self,i):
        start = self.token_stream[self.i]
        identifier = self.token_stream[self.i+1]
        colon = self.token_stream[self.i+2]
        typeOf = self.token_stream[self.i+3]

        if ((identifier[0]=="IDEN") and (colon[0]=="COL") and typeOf[0]=="TYPE"):
            self.i = self.i + 4
            return Var(identifier,typeOf)
        else:
            return None
    
    def parse_assign(self,i):
        


