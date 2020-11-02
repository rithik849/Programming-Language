class Assign:

    def __init__(self,var,value):
        self.var = var
        self.value = value

class Var:

    def __init__(self,var_name,type_name):
        self.name = var_name
        self.type = type_name

class Val:

    def __init__(self,val_name,type_name):
        self.name = val_name
        self.type = type_name

class IntType:

    def __init__(self,val):
        self.val = val

class FloatType:

    def __init__(self,val):
        self.val = val

class BoolType:
    def __init(self,val):
        self.val

class StringType:

    def __init__(self,val):
        self.val

class NoneType:

    def __init__(self):
        self.val = None

class Bin_Op:

    def __init__(self,op,lhs,rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

class While:

    def __init__(self,cond,body):
        self.cond = cond
        self.body = body

class If:

    def __init__(self,cond,body):
        self.cond = cond
        self.body = body

    def __init__(self,cond,cond_body,else_body):
        self.cond = cond
        self.body = cond_body
        self.else_body = else_body

