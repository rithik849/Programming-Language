from symbol_table import SymbolTable


errors = set()


def getErrors():
    return errors

def clearErrors():
    global errors
    errors = set()

class Statements:

    def __init__(self,statements,statement):
        self.statements = statements
        self.statement = statement

    #Generate the symbol table for all statements.
    def generateSymbolTable(self,symbolTable=None):
        global errors
        symbolTable = self.statements.generateSymbolTable(symbolTable)
        symbolTable = self.statement.generateSymbolTable(symbolTable)

        return symbolTable

    #Check for a terminal return statement.
    def hasTerminalReturn(self):
        return self.statement.hasTerminalReturn()

    #Check there is no return statement.
    def hasNoReturn(self):
        return self.statements.hasNoReturn() and self.statement.hasNoReturn()
        
    #Print Parsed Tree. 
    def pp(self):
        return "Seq("+self.statements.pp()+","+self.statement.pp()+")"

    #Python code equivalant of the statement.
    def python_print(self,indent=0):
        tabs = "\t"*indent
        return self.statements.python_print(indent)+"\n"+self.statement.python_print(indent)+"\n"

#Used as a wrapper for types
class Type:

    def __init__(self,val,literal_type):
        self.val = val
        self.type = literal_type

    def generateSymbolTable(self,symbolTable=None):
        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def typecheck(self,symbolTable):
        return self.type

    def pp(self):
        return str(self.val)

    def python_print(self,indent=0):
        tabs = "\t"*indent
        return tabs+str(self.val)

    def __str__(self):
        return str(self.type)

#Stores List elements
class List:
    def __init__(self,elements):
        self.elements = elements

    def generateSymbolTable(self,symbolTable=None):
        self.typecheck(symbolTable)
        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def typecheck(self,symbolTable):
        global errors
        #Check lists have at most 1 type of element
        types = set()
        for element in self.elements:
            types.add(element.typecheck(symbolTable))
        if None in types:
            return None
        if len(types)>1:
            errors.add("All list elements must be of the same type.")
            return None
        if len(types)==0:
            return "[]"
        return "["+list(types)[0]+"]"

    def pp(self):
        list_contents = "["
        counter = 0 
        for element in self.elements:
            list_contents += element.pp()
            counter += 1
            if counter < len(self.elements):
                list_contents += ","
        list_contents += "]"
        return list_contents

    def python_print(self,index=0):
        tabs = "\t"*index
        string = "["
        counter = 0
        for element in self.elements:
            string += element.python_print(index)
            counter += 1
            if counter < len(self.elements):
                string += ","
        string += "]"
        return string
            

#Index used for lists
class Index:
        def __init__(self,id,index):
            self.id = id
            self.list_index = index

        def generateSymbolTable(self,symbolTable=None):
            global errors

            #Check the type of index, and the List or Index being indexed
            if self.list_index.typecheck(symbolTable)!="int":
                errors.add("Index must be of type int")

            self.id.generateSymbolTable(symbolTable)

            return symbolTable

        #Find the type of identifier of the item being indexed
        def getIdenType(self,symbolTable):
            
            if isinstance(self.id,List):
                #If it is a List, it is a literal, so we return the element type
                return List
            elif isinstance(self.id,ID):
                #If it is an ID, we return the type of the identifier
                variableInfo = symbolTable.lookup(self.id.id)
                return variableInfo[2]
            elif isinstance(self.id,Index):
                #If it is an Index we recursively call to find the identifier type.
                return self.id.getIdenType(symbolTable)


        def typecheck(self,symbolTable):
            global errors
            record = self.id.typecheck(symbolTable)

            #Typecheck the element being indexed.

            if record==None:
                return None
            elif record[0:len(record):len(record)-1]=="[]":
                return record[1:len(record)-1]
            else:
                errors.add("Indexing applies only to list type structures.")
                return None
        
        def hasTerminalReturn(self):
            return False

        def hasNoReturn(self):
            return True

        def pp(self):
            return self.id.pp()+"["+self.list_index.pp()+"]"

        def python_print(self,index=0):
            return self.id.python_print(index) + "["+self.list_index.python_print(index)+"]"


#Used with initial assignment. Variable
class Var:

    def __init__(self,var_name,type_name):
        self.name = var_name
        self.type = type_name


    #Used with functions to distinguish if many parameters have the same identifier name
    def __hash__(self):
        return hash((self.name.id,Var))

    def __eq__(self,other):
        return isinstance(other,Var) and self.name.id==other.name.id

    def generateSymbolTable(self,symbolTable=None):
        #Record the identifier and its type in the table
        symbolTable.insert(self.name.id,self.type,"VAR")
        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def pp(self):
        return "Var("+self.name.pp()+","+str(self.type)+")"

    def python_print(self,indent=0):
        tabs = "\t"*indent
        return self.name.python_print()

#Used with initial assignment. Constant
class Val:
    def __init__(self,val_name,type_name):
        self.name = val_name
        self.type = type_name

    def __eq__(self,other):
        return isinstance(other,Val) and self.name.id==other.name.id

    def __hash__(self):
        return hash((self.name.id,Val))
        
    def generateSymbolTable(self,symbolTable=None):
        symbolTable.insert(self.name.id,self.type,"VAL")
        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def pp(self,indent=0):
        return "Val("+self.name.pp()+","+str(self.type)+")"

    def python_print(self,indent=0):
        tabs = "\t"*indent
        return self.name.python_print()

class Assign:

    def __init__(self,var,value):
        self.var = var
        self.value = value

    def generateSymbolTable(self,symbolTable=None):
        global errors
        if isinstance(self.var,ID):
            variableInfo = symbolTable.lookup(self.var.id)
            #Search for the identifier in the table, and check its existence, identity type, and variable type with the value being assigned
            if variableInfo==None:

                errors.add(self.var.id +" is Undefined")
            
            elif variableInfo[2]!="VAR":

                errors.add(variableInfo[0]+": Cannot re-assign to "+variableInfo[2])
            
            elif self.value.typecheck(symbolTable) == None:

                errors.add("Right hand side of assignment to '"+self.var.id+"' has an incorrect assignment")
            
            elif variableInfo[1] != self.value.typecheck(symbolTable):

                if variableInfo[1][0:len(variableInfo[1]):len(variableInfo[1])-1]!="[]" or self.value.typecheck(symbolTable)!="[]":
                    errors.add("Type "+self.value.typecheck(symbolTable)+" can not be assigned to variable of type "+variableInfo[1])
            
        elif isinstance(self.var,Index):
            #Perform type checking
            variable_type = self.var.typecheck(symbolTable)
            value_type = self.value.typecheck(symbolTable)

            self.var.generateSymbolTable(symbolTable)
            self.value.generateSymbolTable(symbolTable)

            if value_type == None:

                errors.add("Right hand side of assignment to list has an incorrect assignment")
            
            elif variable_type!=None and variable_type!=value_type:

                #Allow empty list assignments to be legal to veriables of type list
                if variable_type[0:len(variable_type):len(variable_type)-1]!="[]" or value_type!="[]":
                    
                    errors.add("Type "+self.value.typecheck(symbolTable)+" can not be assigned to variable of type "+self.var.typecheck(symbolTable))
            
            elif self.var.getIdenType(symbolTable)==List:
                
                errors.add("Can not assign to type literal")
            
            elif self.var.getIdenType(symbolTable) not in ["VAR",List]:
                
                errors.add("Can not assign to element of a constant list.")
        else:
            errors.add("Can not assign to a literal")

        self.value.generateSymbolTable(symbolTable)

        return symbolTable


    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def pp(self):
        return self.var.pp()+"["+str(self.value.pp())+"]"

    def python_print(self,indent=0):
        tabs = "\t"*indent
        return tabs+self.var.python_print()+"="+self.value.python_print()

class InitAssign:

    def __init__(self,var,value):
        self.var = var
        self.value = value

    def generateSymbolTable(self,symbolTable=None):
        symbolTable = self.var.generateSymbolTable(symbolTable)
        global errors

        #Ensure we do not initially assign an index.
        if isinstance(self.var.name,Index):
            errors.add("Can not initialise a list index as a variable or constant")

        elif self.value.typecheck(symbolTable)!= self.var.type:
            #If the types do not match, we check if either of them are a list type. If the value is an empty list, we consider the assignment legal.

            if self.var.type[0:len(self.var.type):len(self.var.type)-1]!="[]" or self.value.typecheck(symbolTable)!="[]":
                if self.value.typecheck(symbolTable):
                    errors.add("Can not initialise variable/value of type "+str(self.var.type)+" with value of type "+str(self.value.typecheck(symbolTable)))
                else:
                    errors.add("Incorrect assignment to variable/value of type "+str(self.var.type))
        else:
            self.value.generateSymbolTable(symbolTable)

        self.value.generateSymbolTable(symbolTable)

        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def pp(self):
        return "Init"+self.var.pp()+"["+str(self.value.pp())+"]"

    def python_print(self,indent=0):
        tabs = "\t"*indent
        return tabs+self.var.python_print()+"="+self.value.python_print()


class ID:

    def __init__(self,identifier_name):
        self.id = identifier_name

    def generateSymbolTable(self,symbolTable=None):
        global errors
        #Check the existence of the identifier in the table
        if self.typecheck(symbolTable)==None:
            errors.add("Undefined identifier "+self.id)

        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def typecheck(self,symbolTable):
        global errors
        record = symbolTable.lookup(self.id)
        if record==None:
            return None
        else:
            return symbolTable.lookup(self.id)[1]

    def pp(self):
        return "ID("+str(self.id)+")"

    def python_print(self,indent=0):
        tabs = "\t"*indent
        return tabs+str(self.id)

class Bin_Op:

    def __init__(self,op,lhs,rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def generateSymbolTable(self,symbolTable=None):
        global errors

        #Check the type of the expression
        if self.typecheck(symbolTable)==None:

            #If there is an error with the lhs, we perform a check. Vice versa with rhs.
            if self.lhs.typecheck(symbolTable)==None:
                self.lhs.generateSymbolTable(symbolTable)

            if self.rhs.typecheck(symbolTable)==None:
                self.rhs.generateSymbolTable(symbolTable)

            #If both sides do not typecheck to None we have found the source of ther error of the expression
            if (self.lhs.typecheck(symbolTable)!=None and self.rhs.typecheck(symbolTable)!=None):
                errors.add("Binary Operator "+self.op+" not callable between parameters of type "+self.lhs.typecheck(symbolTable)+" and "+self.rhs.typecheck(symbolTable))

        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def typecheck(self,symbolTable):
        lhs_type = self.lhs.typecheck(symbolTable)
        rhs_type = self.rhs.typecheck(symbolTable)
        #If we have types for both sides, we check if theyh are lists
        if lhs_type!=None and rhs_type!=None:
            if self.op=="+" and lhs_type[0:len(lhs_type):len(lhs_type)-1]=="[]" and rhs_type[0:len(rhs_type):len(rhs_type)-1]=="[]":
                #We check if one of the sides is an empty list, in order to determine the type of the expression
                if lhs_type!=rhs_type:

                    if lhs_type!="[]" and rhs_type!="[]":
                        return None
                    elif lhs_type=="[]":
                        return rhs_type
                    else:
                        return lhs_type
        #If any side is typechecked to None, we return None
        if lhs_type==None or rhs_type==None:
            return None
        #String concatonation
        elif self.op=="+" and lhs_type=="str" and rhs_type=="str":
            return "str"
        elif self.op=="+" and lhs_type=="str" and rhs_type!="str":
            return None
        elif self.op=="+" and lhs_type!="str" and rhs_type=="str":
            return None
        #For math operators
        elif self.op in ["+","-","*","/","^","%"]:
            #If there is a division of numbers, we return float
            if self.op=="/" and lhs_type in set(["int","float"]) and rhs_type in set(["int","float"]):
                return "float"
            #Used for operations between floats and integers, or possibly between two lists that both contain elements
            elif lhs_type==rhs_type and (lhs_type in ["float","int"] or (lhs_type[0:len(lhs_type):len(lhs_type)-1]=="[]")):
                return lhs_type
            #If one side is a float, we return float
            elif lhs_type in set(["float","int"]) and rhs_type in set(["float","int"]) - set([lhs_type]):
                return "float"
            else:
                return None
        #Comparison operators
        elif self.op in ["<",">=","<=",">","!=","=="]:

            #Comparison between integers and or floats
            if self.lhs.typecheck(symbolTable) in ["int","float"] and self.rhs.typecheck(symbolTable) in ["int","float"]:
                return "bool"
            #With equality, we can compare any types
            elif self.op in ["==","!="]:
                return "bool"
            else:
                return None
        #Boolean operators
        elif self.op in ["||","&&"]:

            #As long as both sides are boolean, we return a type of boolean
            if self.lhs.typecheck(symbolTable)=="bool" and self.rhs.typecheck(symbolTable)=="bool":
                return "bool"
            else:
                return None

    def pp(self):
        return str(self.op)+"("+self.lhs.pp()+","+self.rhs.pp()+")"

    def python_print(self,indent=0):
        tabs = "\t" * indent
        if (self.op=="^"):
            op = "**"
        elif (self.op=="||"):
            op=" or "
        elif (self.op=="&&"):
            op=" and "
        else:
            op = str(self.op)
        return tabs+"("+self.lhs.python_print()+op+self.rhs.python_print()+")"

class Unary_Op:

    def __init__(self,op,rhs):
        self.op = op
        self.rhs = rhs

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def generateSymbolTable(self,symbolTable=None):
        #Check the type of the expression and all its components, until the source of the error is found
        if self.typecheck(symbolTable)==None:

            if self.rhs.typecheck(symbolTable)==None:
                self.rhs.generateSymbolTable(symbolTable)
            else:
                errors.add("Unary Operator "+self.op+" not callable with parameter "+self.rhs.typecheck(symbolTable))

        return symbolTable

    def typecheck(self,symbolTable):
        #Typechecking for mathematical operators and boolean operators
        if self.op in ["-"] and self.rhs.typecheck(symbolTable) in ["float","int"]:
            return self.rhs.typecheck(symbolTable)
        elif self.op=="!" and self.rhs.typecheck(symbolTable)=="bool":
            return "bool"
        else:
            return None

    def pp(self):
        return str(self.op)+"("+self.rhs.pp()+")"

    def python_print(self,indent=0):
        tabs = "\t" * indent
        if self.op == "!":
            return tabs+"not "+"("+str(self.rhs.python_print())+")"
        elif self.op in ["-"]:
            return tabs+self.op+self.rhs.python_print()

class Print:

    def __init__(self,param=""):
        self.param = param

    def generateSymbolTable(self,symbolTable=None):
        #Check the parameters type
        self.param.generateSymbolTable(symbolTable)

        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def pp(self):
        return "print("+self.param.pp()+")"

    def python_print(self,indent=0):
        tabs = "\t" * indent
        return tabs+"print("+self.param.python_print()+")"


class While:

    def __init__(self,cond,body):
        self.cond = cond
        self.body = body

    def generateSymbolTable(self,symbolTable=None):
        global errors
        #Check the type of the condition, and create a scope for the while block
        if self.cond.typecheck(symbolTable)!="bool":
            errors.add("Conditional parameter to while must be of type bool")

        bodyTable = SymbolTable(symbolTable,symbolTable.functionRecord)
        self.body.generateSymbolTable(bodyTable)

        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return self.body.hasNoReturn()

    def pp(self):
        return "While("+self.cond.pp()+","+self.body.pp()+")"
    
    def python_print(self,indent =0):
        tabs = "\t"*indent
        return tabs+"while "+self.cond.python_print()+":\n"+self.body.python_print(indent+1)+"\n"

class For:

    def __init__(self,id,start_val,end_val,body):
        self.identifier = id
        self.start_value = start_val
        self.end_value = end_val
        self.body = body

    def generateSymbolTable(self,symbolTable):
        global errors

        #Check the start and end values of the for loop and create a scope for the for block
        if self.start_value.typecheck(symbolTable)!= "int":
            errors.add("Start value of for loop must be of type int")

        if self.end_value.typecheck(symbolTable)!= "int":
            errors.add("End value of for loop must be of type int")

        bodyTable = SymbolTable(symbolTable,symbolTable.functionRecord)
        #We add the identifier into the body block
        bodyTable.insert(self.identifier.id,"int","VAR")
        self.body.generateSymbolTable(bodyTable)

        return symbolTable

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return self.body.hasNoReturn()

    def pp(self):
        return "For("+self.start_value.pp()+","+self.end_value.pp()+"):"+self.body.pp()

    def python_print(self,indent=0):
        tabs = "\t" * indent
        return tabs+"for "+self.identifier.python_print()+" in range("+self.start_value.python_print()+","+self.end_value.python_print()+"):\n"+self.body.python_print(indent+1)

class If:

    def __init__(self,cond,cond_body,else_body=None):
        self.cond = cond
        self.body = cond_body
        self.else_body = else_body

    def generateSymbolTable(self,symbolTable=None):
        global errors
        #Check the condition and create seperate scopes for the body and else (if there is an else block)
        if self.cond.typecheck(symbolTable)!="bool":
            errors.add("Conditional parameter to conditional must be of type bool")

        #Different scopes for each body
        bodyTable = SymbolTable(symbolTable,symbolTable.functionRecord)
        self.body.generateSymbolTable(bodyTable)

        if self.else_body:
            elseBodyTable = SymbolTable(symbolTable,symbolTable.functionRecord)
            self.else_body.generateSymbolTable(elseBodyTable)
        return symbolTable

    #Check for terminal returns in both blocks
    def hasTerminalReturn(self):
        return self.body.hasTerminalReturn() and ((not self.else_body) or self.else_body.hasTerminalReturn())

    #Check for return values in both blocks
    def hasNoReturn(self):
        return self.body.hasNoReturn() and ((not self.else_body) or self.else_body.hasNoReturn())

    def pp(self):
        if (self.else_body):
            return "If("+self.cond.pp()+","+self.body.pp()+","+self.else_body.pp()+")"
        else:
            return "If("+self.cond.pp()+","+self.body.pp()+")"

    def python_print(self,indent=0):
        tabs = "\t" * indent
        if (self.else_body):
            return tabs+"if "+self.cond.python_print()+":\n"+self.body.python_print(indent+1)+"\n"+tabs+"else:\n"+self.else_body.python_print(indent+1)+"\n"
        else:
            return tabs+"if "+self.cond.python_print()+":\n"+self.body.python_print(indent+1)+"\n"

class Return:

    def __init__(self,identifier):
        self.ret_val = identifier

    def python_print(self,indent=0):
        tabs = "\t" * indent
        return tabs+"return "+self.ret_val.python_print()

    def hasTerminalReturn(self):
        return True

    def hasNoReturn(self):
        return False

    def pp(self):
        return "Ret("+str(self.ret_val.pp())+")"

    def generateSymbolTable(self,symbolTable=None):
        global errors
        if (not symbolTable.parentTable):
            errors.add("Return statement must be within a function")

        #Get the function of which the symbol table is in.
        functionRec = symbolTable.getFunctionEntry()
        if functionRec:
            functionType = functionRec[1]
            idenType = functionRec[2]

            #Check if it is a function
            if idenType=="FUNC":
                if self.ret_val.typecheck(symbolTable)==None:
                    #If the returned expression is erroneous we check its components
                    self.ret_val.generateSymbolTable(symbolTable)

                elif (self.ret_val.typecheck(symbolTable) != functionType):
                    #Empty list check
                    if functionType[0:len(functionType):len(functionType)-1]!="[]" or self.ret_val.typecheck(symbolTable)!="[]":
                        errors.add("Returned value of type "+self.ret_val.typecheck(symbolTable)+" does not match function type "+functionType)
            
            else:
                errors.add("Return statement must be in a function")
        else:
            errors.add("Return statement must be within a function")

        return symbolTable

class Call:

    def __init__(self,function_identifier,argument_list):
        self.identifier = function_identifier
        self.argument_list = argument_list

    def generateSymbolTable(self,symbolTable=None):
        self.typecheck(symbolTable)
        return symbolTable

    def typecheck(self,symbolTable):
        global errors
        record = symbolTable.lookup(self.identifier.id)
        

        errorLocation = "Function Call of "+self.identifier.id+": "

        #Function calls for type casting, or inbuilt functions
        if record==None:
        
            if self.identifier.id=="len":
                argument_count = len(self.argument_list)

                if argument_count==1:
                    argument_type = self.argument_list[0].typecheck(symbolTable)

                    #If the argument is a list return the number of elements as an integer
                    if argument_type!=None and argument_type[0:len(argument_type):len(argument_type)-1]=="[]":
                        return "int"
                    else:
                        errors.add(errorLocation+"len can only be used with parameters of type list")
                else:
                    errors.add(errorLocation+"1 parameter expected but found "+str(argument_count))
                return None

            elif self.identifier.id in ["str","bool"]:

                #If the function is a string or boolean, it can accept any argument type.
                argument_count = len(self.argument_list)
                if argument_count==1:
                    return self.identifier.id
                else:
                    errors.add(errorLocation+"1 parameter expected but found "+str(argument_count))
                return None

            elif self.identifier.id in ["int","float"]:

                #If the function is an integer or float check if the argument is an integer or float.
                argument_count = len(self.argument_list)
                if argument_count==1:
                    argument_type = self.argument_list[0].typecheck(symbolTable)

                    if argument_type in ["int","float"]:
                        return self.identifier.id
                    else:
                        errors.add(errorLocation+self.identifier.id+" can only be used with parameters of type int and float")
                
                else:
                    errors.add(errorLocation+"1 parameter expected but found "+str(argument_count))
                return None

        #Checking function exists in symbolTable.
        if record:
            #Check if the identifier is a function with the correct number and types of arguments.
            if record[2]=="FUNC":
                parameters = record[4]

                if len(parameters)==len(self.argument_list):
                    mismatchFound = False
                    counter = 0

                    while not mismatchFound and counter<len(parameters):
                        #Perform checks on erroneous arguments
                        if self.argument_list[counter].typecheck(symbolTable)==None:
                            mismatchFound = True
                            errors.add(errorLocation+"Argument does not match type "+parameters[counter].type+" of parameter "+parameters[counter].name.id)
                            self.argument_list[counter].generateSymbolTable(symbolTable)
                            
                        elif self.argument_list[counter].typecheck(symbolTable)!=parameters[counter].type:
                            param_type = parameters[counter].type
                            argument_type = self.argument_list[counter].typecheck(symbolTable)
                            #Allow empty lists as a parameter
                            if argument_type!="[]" or param_type[0:len(param_type)-1:len(param_type)]!="[]":
                                mismatchFound = True
                                errors.add(errorLocation+"Type mismatch for parameter "+parameters[counter].name.id+" of type "+parameters[counter].type+" with argument of type "+str(self.argument_list[counter].typecheck(symbolTable)))
                            
                        counter = counter + 1

                    if mismatchFound:
                        return None

                else:
                    errors.add(errorLocation+str(len(parameters))+" parameters expected but "+str(len(self.argument_list))+" given")
                    return None
                
                return record[1]
            else:
                errors.add(errorLocation+""+self.identifier.id+" is not a function")
        else:
            errors.add("Function "+self.identifier.id+" not found")
        return None

    def hasTerminalReturn(self):
        return False

    def hasNoReturn(self):
        return True

    def pp(self):
        arguments = ""
        for argument in self.argument_list:
            arguments = arguments + argument.pp()
            if argument != self.argument_list[-1]:
                arguments += ","

        return "CALL "+self.identifier.pp()+"("+arguments+")"
        

    def python_print(self,indent=0):
        tabs = "\t"*indent
        arguments = ""
        for argument in self.argument_list:
            arguments = arguments + argument.python_print()
            if argument != self.argument_list[-1]:
                arguments += ","
        return tabs+self.identifier.python_print()+"("+arguments+")"


class Function:

    def __init__(self,identifier,parameter_list,return_type,body):
        self.name = identifier
        self.parameter_list = parameter_list
        self.return_type = return_type
        self.body = body

    def generateSymbolTable(self,symbolTable=None):
        global errors
        #Create a symbol table for the body
        childTable = SymbolTable(symbolTable)
        entry = (self.name.id,self.return_type,"FUNC",childTable,self.parameter_list)
        
        #Set the function record, which will be used to check return statements in the body
        childTable.setFunctionEntry((self.name.id,self.return_type,"FUNC",childTable,self.parameter_list))

        errorLocation = "Function Declaration of "+self.name.id+": "
        
        #Check if the function is declared within another function
        if symbolTable.getFunctionEntry():
            errors.add(errorLocation+"Function can not be defined within another function")

        #Check there are no repeated parameter names. __hash__ __eq__ at Var class
        parameters = set(self.parameter_list)

        if len(parameters)!=len(self.parameter_list):
            errors.add(errorLocation+"Repeated parameters in function definition of "+self.name.id)

        #Generate parameter entries within the child table.
        for parameter in self.parameter_list:
            childTable = parameter.generateSymbolTable(childTable)

        #If we have none type function we have no return statement in the function body, otherwise we do have a terminal return statement
        if self.return_type!="none" and not self.body.hasTerminalReturn():
            errors.add(errorLocation+"Function "+self.name.id+" does not have a terminal return statement")
        elif self.return_type=="none" and not self.body.hasNoReturn():
            errors.add(errorLocation+"Function "+self.name.id+" has a return statement")

        symbolTable.insert(entry[0],entry[1],entry[2],entry[3],entry[4])
        self.body.generateSymbolTable(childTable)

        
        return symbolTable

    def hasTerminalReturn(self):
        return self.body.hasTerminalReturn()

    def hasNoReturn(self):
        return self.body.hasNoReturn()

    def pp(self):
        parameters = ""
        for parameter in self.parameter_list:
            parameters = parameters + parameter.pp()

            if parameter != self.parameter_list[-1]:
                parameters += ","

        return "DEF "+self.name.pp()+"("+parameters+") : "+str(self.return_type)+"{"+self.body.pp()+"}"

    def python_print(self,indent=0):
        tabs = "\t" * indent

        parameters = ""
        for parameter in self.parameter_list:
            parameters = parameters + parameter.python_print()

            if parameter != self.parameter_list[-1]:
                parameters += ","

        return tabs+"def "+self.name.python_print()+"("+parameters+"):\n"+self.body.python_print(indent+1)+"\n"