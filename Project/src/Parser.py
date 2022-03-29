
#Library yacc taken from ply package
import ply.yacc as yacc

from SemanticAnalyzer import *
from LexAnalyzer import tokens

#Library time imported from python standard library
import time

#Defines the order of precedence for operators
precedence = (
("nonassoc","LESS","GREATER","LESS_EQUAL","GREATER_EQUAL","EQUAL","NOT_EQUAL"),    
("left","OR"),
("left","AND"),
("left","NOT"),
("left","ADD","SUB"),
("left","MUL","DIV","MOD"),
("right","POW"),
('right','USUB'))


def p_error(p):
    #If statement to ignore comments
    if p:
        getErrors().add("Line "+str(p.lineno)+":Syntax Error at "+ str(p.value))


def p_statements(p):
    '''
    statements : statements statement
    '''
    p[0] = Statements(p[1],p[2])

def p_statements_terminal(p):
    '''
    statements : statement
    '''
    p[0] = p[1]

def p_statement(p):
    '''
    statement : assignment
    statement : selection
    statement : print
    statement : while_loop
    statement : for_loop
    statement : func_definition
    statement : return_statement
    statement : expression
    '''
    p[0] = p[1]

def p_negative_number(p):
    '''expression : SUB expression %prec USUB
       expression : NOT expression'''
    p[0] = Unary_Op(p[1],p[2])

def p_relations(p):
    '''
    relation : LESS
    relation : GREATER
    relation : LESS_EQUAL
    relation : GREATER_EQUAL
    relation : EQUAL
    relation : NOT_EQUAL
    '''
    p[0]=p[1]

def p_expression_math(p):
    '''expression : expression ADD expression
       expression : expression SUB expression
       expression : expression MUL expression
       expression : expression DIV expression
       expression : expression MOD expression
       expression : expression POW expression
       expression : expression AND expression
       expression : expression OR expression
       expression : expression relation expression
    '''
    p[0] = Bin_Op(p[2],p[1],p[3])

def p_iden_expression(p):
    '''iden_expression : identifier
    iden_expression : func_call'''

    p[0] = p[1]

def p_variable(p):
    '''expression : iden_expression'''

    p[0] = p[1]

def p_expression_bracket(p):
    '''expression : L_PAR expression R_PAR
    '''
    p[0] = p[2]

def p_list(p):
    '''list : L_BRACE argument_list R_BRACE'''

    p[0] = List(p[2])

def p_string(p):
    '''string : STRING'''
    p[0] = Type(p[1],"str")

def p_int(p):
    '''int : INT'''
    p[0] = Type(p[1],"int")

def p_float(p):
    '''float : FLOAT'''
    p[0] = Type(p[1],"float")

def p_bool(p):
    '''bool : BOOL'''
    p[0] = Type(p[1],"bool")

def p_primary(p):
    '''expression : list
    expression : int
    expression : bool
    expression : float
    expression : string
    expression : list_index'''
    p[0] = p[1]

def p_list_index(p):
    '''list_index : list L_BRACE expression R_BRACE
    list_index : identifier L_BRACE expression R_BRACE
    list_index : list_index L_BRACE expression R_BRACE
    '''

    p[0] = Index(p[1],p[3]) 

def p_base_type(p):
    '''
    base_type : INT_TYPE
    base_type : FLOAT_TYPE
    base_type : BOOL_TYPE
    base_type : STRING_TYPE
    '''

    p[0] = p[1]

def p_type(p):
    '''type : base_type'''

    p[0] = p[1]

def p_list_type(p):
    ''' 
    type : L_BRACE type R_BRACE'''

    p[0] = "["+p[2]+"]"

def p_var_initialize(p):
    '''
    var_init : VAR identifier COL type
    '''
    p[0] = Var(p[2],p[4])

def p_val_initialize(p):
    '''
    val_init : VAL identifier COL type
    '''
    p[0] = Val(p[2],p[4])

def p_init(p):
    '''
    initialize : val_init
    initialize : var_init
    '''
    p[0] = p[1]

def p_identifier(p):
    '''
    identifier : IDEN
    '''

    p[0] = ID(p[1])

def p_assigned(p):
    '''
    assign : expression'''

    p[0] = p[1]

def p_init_assign(p):
    '''
    assignment : initialize ASSIGNMENT assign
    '''

    p[0] = InitAssign(p[1],p[3])

def p_assign(p):
    '''
    assignment : identifier ASSIGNMENT assign
    assignment : list_index ASSIGNMENT assign
    assignment : expression ASSIGNMENT assign
    '''
    p[0] = Assign(p[1],p[3])



def p_else_selection(p):
    '''
    selection : IF expression L_SCOPE statements R_SCOPE ELSE L_SCOPE statements R_SCOPE
    '''
    p[0] = If(p[2],p[4],p[8])

def p_selection(p):
    '''
    selection : IF expression L_SCOPE statements R_SCOPE
    '''
    p[0] = If(p[2],p[4])

def p_while_loop(p):
    '''
    while_loop : WHILE expression L_SCOPE statements R_SCOPE
    '''
    p[0] = While(p[2],p[4])

def p_for_loop(p):
    '''
    for_loop : FOR identifier ASSIGNMENT expression TO expression L_SCOPE statements R_SCOPE
    '''

    p[0] = For(p[2],p[4],p[6],p[8])

def p_print(p):
    '''
    print : PRINT L_PAR expression R_PAR
    print : PRINT L_PAR string R_PAR
    '''

    p[0] = Print(p[3])

def p_method_statements(p):
    '''
    method_statements : method_statements method_body
    '''
    p[0] = Statements(p[1],p[2])

def p_method_statement(p):
    '''
    method_statements : method_body
    '''
    p[0]=p[1]

def p_body(p):
    '''
    method_body : statement
    '''

    p[0] = p[1]

def p_return_statement(p):
    '''return_statement : RET expression'''

    p[0] = Return(p[2])

def p_parameter_list(p):
    '''parameter_list : parameter_list COMMA parameter'''
    p[0] = p[1] + p[3]

def p_parameter_list_terminal(p):
    '''parameter_list : parameter'''

    p[0] = p[1]

def p_parameter(p):
    '''parameter : identifier COL type'''

    p[0] = [Var(p[1],p[3])]

def p_parameter_list_empty(p):

    '''parameter_list : '''
    p[0] = []

def p_argument_list(p):
    '''argument_list : argument_list COMMA argument'''

    p[0] = p[1] + p[3]

def p_argument_list_terminal(p):
    '''argument_list : argument'''

    p[0] = p[1]

def p_argument(p):
    '''argument : expression'''

    p[0] = [p[1]]

def p_argument_list_empty(p):
    '''argument : '''

    p[0] = []

def p_function_definition(p):
    '''
    func_definition : DEF identifier L_PAR parameter_list R_PAR COL type L_SCOPE method_statements R_SCOPE
    func_definition : DEF identifier L_PAR parameter_list R_PAR COL NONE_TYPE L_SCOPE method_statements R_SCOPE
    '''

    p[0] = Function(p[2],p[4],p[7],p[9])

def p_function_call(p):
    '''func_call : identifier L_PAR argument_list R_PAR'''

    p[0] = Call(p[1],p[3])

def p_function_cast_call(p):
    '''func_call : base_type L_PAR argument_list R_PAR'''

    p[0] = Call(ID(p[1]),p[3])

parser = yacc.yacc(errorlog=yacc.NullLogger())

#Used for testing
def comp_test(code):
    result = None
    result = parser.parse(code)
    #Lexical/Syntax Errors
    if len(getErrors())==0 and result!=None:
        table = result.generateSymbolTable(SymbolTable())
        code = result.python_print()
        #Semantic Errors
        if (len(getErrors())==0):
            #Runtime Errors
            try:
                #Alows for recursion during execution.
                glob= {}
                compile_code = compile(code,"<string>","exec")
                exec(compile_code,glob)
            except IndexError:
                getErrors().add("Runtime Error : Index out of bounds.")
            except ZeroDivisionError:
                getErrors().add("Runtime Error : Can not divide by 0.")
            except Exception:
                 getErrors().add("Runtime Error : Runtime exception found.")
    return result

#Used for compiling
def comp_file(filename,parse_tree = False, symbolTbl = False,pythonCode = False,duration = False):
    start = 0
    result = None

    if duration:
        start = time.time()

    #Open the file
    try:
        with open(filename,"r") as file:
            content = file.read()
        result = parser.parse(content)
    except IOError:
        print("File not found")

    #Syntax/Lexical Errrors
    if len(getErrors())==0 and result!=None:

        #Print the parse tree if the option is given
        if parse_tree:
            print("Parse Tree:")
            print(result.pp())

        #Generate the symbolTable and perform type checking
        table = result.generateSymbolTable(SymbolTable())

        #Print the symbol table if the option is given
        if symbolTbl:
            print("Symbol Table:")
            print(table.getRoot().printTable())

        code = result.python_print()

        #print the python code if the option is given
        if pythonCode:
            print("Python Equivalant:")
            print(code)
        #Semantic Errors
        if (len(getErrors())==0):
            #Runtime Errors
            try:
                #Alows for recursion during execution.
                glob= {}
                compile_code = compile(code,filename,"exec")
                print("Output:")
                exec(compile_code,glob)
            except IndexError:
                getErrors().add("Runtime Error : Index out of bounds.")
            except ZeroDivisionError:
                getErrors().add("Runtime Error : Can not divide by 0.")
            except Exception:
                 getErrors().add("Runtime Error : Runtime exception found.")

    #If there are errors print them to the user.
    if (len(getErrors())>0):
        print("ERRORS:")
        for error in getErrors():
            print("\n"+error)

    clearErrors()

    #Print the duration of execution if the option is given
    if duration:
        print("DURATION OF EXECUTION:")
        print(time.time()-start)