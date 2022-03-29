import unittest
import sys
sys.path.append("../src")

from SemanticAnalyzer import *
from LexAnalyzer import *
from symbol_table import *
from Parser import *

#Tests SymbolTable defined in symbol_table.py
class SymbolTableTest(unittest.TestCase):

    def setUp(self):
        self.symbolTable = SymbolTable()
        self.childTableTest = SymbolTable(self.symbolTable)
        self.grandChildTable = SymbolTable(self.childTableTest)

    def test_initialisation(self):
        self.assertEquals(self.childTableTest.getParent(),self.symbolTable)

    def test_root(self):
         self.assertEquals(self.grandChildTable.getRoot(),self.symbolTable)

    def test_functionEntry(self):
        functionEntry = ("a","int","FUNC")
        self.grandChildTable.setFunctionEntry(functionEntry)
        self.assertEquals(self.grandChildTable.getFunctionEntry(),functionEntry)

    def test_insert_lookup(self):
        #Test entry
        self.childTableTest.insert("test","str","VAR")
        self.assertEquals(self.childTableTest.lookup("test"),("test","str","VAR",None,[]))
        self.assertEquals(self.grandChildTable.lookup("test"),("test","str","VAR",None,[]))
        
        #Test overwrite entry
        self.childTableTest.insert("test","int","VAL")
        self.assertEquals(self.childTableTest.lookup("test"),("test","int","VAL",None,[]))
        self.assertEquals(len(self.childTableTest.symbols),1)
        
        #Test new entry
        self.childTableTest.insert("test_var","int","VAL")
        self.assertEquals(len(self.childTableTest.symbols),2)

        self.grandChildTable.insert("test","int","VAL")
        self.assertEquals(len(self.grandChildTable.symbols),1)

    def tearDown(self):
        self.symboTable =None


#Tests Classes in SemanticAnalyzer.py
class NodeTest(unittest.TestCase):

    def setUp(self):
        self.test_tbl = SymbolTable()

    def test_type(self):
        test = Type("Hello World!","str")
        
        self.assertEquals(test.val,"Hello World!")
        self.assertEquals(test.type,"str")
        self.assertEquals(test.typecheck(self.test_tbl),"str")
        self.assertEquals(test.python_print(),"Hello World!")
        self.assertEquals(test.python_print(1),"\tHello World!")

    def test_id(self):
        self.test_tbl.insert("a","int","VAL")

        test = ID("a")

        self.assertEquals(test.typecheck(self.test_tbl),"int")
        self.assertEquals(test.generateSymbolTable(self.test_tbl),self.test_tbl)

        test_error = ID("b")
        self.assertEquals(test_error.typecheck(self.test_tbl),None)
        self.assertEquals(test_error.generateSymbolTable(self.test_tbl),self.test_tbl)
        self.assertIn("Undefined identifier b",getErrors())

    def test_var(self):
        test = Var(ID("tmp"),"bool")
        test.generateSymbolTable(self.test_tbl)
        self.assertIn( ("tmp","bool","VAR",None,[]) , self.test_tbl.symbols )

    def test_val(self):
        test = Val(ID("tmp"),"float")
        test.generateSymbolTable(self.test_tbl)
        self.assertIn( ("tmp","float","VAL",None,[]) , self.test_tbl.symbols )

    def test_list(self):

        test = List([Type("","str"),Type("string","str")])
        self.assertEquals(test.generateSymbolTable(self.test_tbl),self.test_tbl)
        self.assertEquals(test.typecheck(self.test_tbl),"[str]")

        test_empty = List([])
        self.assertEquals(test_empty.typecheck(self.test_tbl),"[]")

        test_error = List([Type("","int"),Type("string","str")])
        self.assertEquals(test_error.typecheck(self.test_tbl),None)
        self.assertIn("All list elements must be of the same type.",getErrors())
        self.assertEquals(len(getErrors()),1)

        self.assertEquals(test.hasTerminalReturn(),False)
        self.assertEquals(test.hasNoReturn(),True)

        self.assertEquals(test_empty.python_print(),"[]")
        self.assertEquals(test.python_print(),"[,string]")

    def test_index(self):
        test_list = List([Type("","str"),Type("string","str")])
        
        test =Index(test_list,Type(4,"int"))

        self.assertEquals(test.generateSymbolTable(self.test_tbl),self.test_tbl)
        
        #Test the wrong parameter type being passed as an index
        test_2d_list_error = Index(test,Type('3',"str"))
        test_2d_list_error.generateSymbolTable(self.test_tbl)

        self.assertIn("Index must be of type int",getErrors())
        #Test that getIdenType returns the List class when indexing a list.
        self.assertEquals(test.getIdenType(self.test_tbl),List)

        clearErrors()
        
        #Test that using 2 indexes is possible.
        test_2d_list = Index(test,Type('3',"int"))
        test_2d_list.generateSymbolTable(self.test_tbl)

        self.assertEquals(getErrors(),set())
        self.assertEquals(test_2d_list.getIdenType(self.test_tbl),List)


        #Test indexing throws an error with non-list types.
        test_typecheck = Index(Type("erroneous","str"),Type(2,"int"))

        self.assertEquals(test_typecheck.typecheck(self.test_tbl),None)
        self.assertIn("Indexing applies only to list type structures.",getErrors())

    def test_init_assign(self):

        #Can assign a list
        test = InitAssign( Var(ID("iden"),"[int]"),List( [Type(4,"int")] ) )
        test.generateSymbolTable(self.test_tbl)

        self.assertIn( ("iden","[int]","VAR",None,[]) ,self.test_tbl.symbols)

        #Can assign an empty list
        test = InitAssign( Var(ID("iden"),"[str]"),List( [] ) )
        test.generateSymbolTable(self.test_tbl)

        self.assertIn( ("iden","[str]","VAR",None,[]) ,self.test_tbl.symbols)

        #Test that Indexes can not be used in the left hand side of a variable or constant declaration
        test = InitAssign( Var(Index(ID("iden"),Type(0,"int")),"int") , Type("test","int"))

        test.generateSymbolTable(self.test_tbl)

        self.assertIn("Can not initialise a list index as a variable or constant",getErrors())

        test_error = InitAssign( Var(ID("a"),"str"),Type("Test String","str") )
        test_list_error = InitAssign( Var(ID("iden"),"[int]"),List( [ID("a")] ) )
        
        #Test an error is given when there is a type mismatch.
        test_list_error.generateSymbolTable(self.test_tbl)
        
        self.assertIn("Incorrect assignment to variable/value of type [int]",getErrors())
        clearErrors()
        
        test_error.generateSymbolTable(self.test_tbl)
        test_list_error.generateSymbolTable(self.test_tbl)

        self.assertIn("Can not initialise variable/value of type [int] with value of type [str]",getErrors())

    def test_assign(self):
        #Test Error Branches
        test = Assign(Type(4,"int"),Type(True,"bool"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Can not assign to a literal",getErrors())

        test = Assign(ID("b"),Type(3,"int"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("b is Undefined",getErrors())

        test_val = Val(ID("b"),"float")
        test_val.generateSymbolTable(self.test_tbl)
        test = Assign(ID("b"),Type(2.3,"float"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("b: Cannot re-assign to VAL",getErrors())
        
        test_val = Var(ID("b"),"bool")
        test_val.generateSymbolTable(self.test_tbl)
        test = Assign(ID("b"),ID("a"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Right hand side of assignment to 'b' has an incorrect assignment",getErrors())

        test = Assign(ID("b"),Type(3,"int"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Type int can not be assigned to variable of type bool",getErrors())

        clearErrors()

        #Testing assignment with Indexes

        #Assigning an undefined identifier
        test_val = Var(ID("listOfNumbers"),"[float]")
        test_val.generateSymbolTable(self.test_tbl)
        test = Assign(Index(ID("listOfNumbers"),Type(0,"int")),ID("c"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Right hand side of assignment to list has an incorrect assignment",getErrors())

        #Assigning wrong type
        test = Assign(Index(ID("listOfNumbers"),Type(0,"int")),Type(2,"int"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Type int can not be assigned to variable of type float",getErrors())

        #Assigning to a list literal
        test = Assign(Index(List([Type(9,"int")]),Type(0,"int")),Type(2,"int"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Can not assign to type literal",getErrors())

        #Assigning to a constant
        test_val = Val(ID("constantList"),"[int]")
        test_val.generateSymbolTable(self.test_tbl)
        test = Assign(Index(ID("constantList"),Type(0,"int")),Type(3,"int"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Can not assign to element of a constant list.",getErrors())
        clearErrors()
        
        #Test assigning an empty list
        test = Assign(ID("listOfNumbers"),List([]))
        test.generateSymbolTable(self.test_tbl)

        #Assigning a list to a list variable
        test = Assign(ID("listOfNumbers"),List([Type(3.4,"float")]))
        test.generateSymbolTable(self.test_tbl)

        #Assign a value to an index.
        test = Assign(Index(ID("listOfNumbers"),Type(0,"int")),Type(2.0,"float"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(getErrors(),set())

    def test_binary_op(self):

        #Test with integer and float typed correctly
        test = Bin_Op("+",Type(3,"int"),Type(2.0,"float"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals("float",test.typecheck(self.test_tbl))
        self.assertEquals(0,len(getErrors()))

        #Test with bool and float gives an error
        test = Bin_Op("+",Type(3,"bool"),Type(2.0,"float"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(None,test.typecheck(self.test_tbl))
        self.assertIn("Binary Operator + not callable between parameters of type bool and float",getErrors())
        
        #Test that list concatonation works in correct use
        test = Bin_Op("+",List([Type(3,"float")]),List([Type(2.0,"float")]))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals("[float]",test.typecheck(self.test_tbl))

        #Test that list concatonation detects incorrect use
        test = Bin_Op("+",List([Type(3,"float")]),List([Type("2.0","str")]))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(None,test.typecheck(self.test_tbl))
        self.assertIn("Binary Operator + not callable between parameters of type [float] and [str]",getErrors())

        #Test string concatonation works
        test = Bin_Op("+",Type("Hello ","str"),Type("World","str"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals("str",test.typecheck(self.test_tbl))

        clearErrors()

        #Test multiple binary operations used incorrectly give the correct error messages.
        test = Bin_Op("+",Bin_Op("+",Type("This","str"),Type(3,"int")),Bin_Op("+",Type(2,"int"),Type("is","str")))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(None,test.typecheck(self.test_tbl))
        self.assertEquals(2,len(getErrors()))

        clearErrors()

        #Test division typechecks to a float
        test = Bin_Op("/",Type(3,"int"),Type(2,"int"))
        self.assertEquals(test.typecheck(self.test_tbl),"float")

        test = Bin_Op("/",Type(3,"int"),Type(2.0,"float"))
        self.assertEquals(test.typecheck(self.test_tbl),"float")

        #Test Modulo
        test = Bin_Op("%",Bin_Op("-",Type(3,"int"),Type(5,"float")),Type(5,"int"))
        self.assertEquals(test.typecheck(self.test_tbl),"float")

        #Test comparison operators
        for operator in ["<",">","<=",">=","!=","=="]:
            test = Bin_Op(operator,Type(4,"int"),Type(6,"float"))
            self.assertEquals(test.typecheck(self.test_tbl),"bool")

        test = Bin_Op("==",Bin_Op("<",Type(4,"int"),Type(6.0,"float")),Bin_Op(">=",Type(4,"int"),Type(6,"int")) )
        self.assertEquals(test.typecheck(self.test_tbl),"bool")

        test = Bin_Op("!=",Type("test","str"),Type(0,"int"))
        self.assertEquals(test.typecheck(self.test_tbl),"bool")

        #Test boolean operators
        for operator in ["||","&&"]:
            test = Bin_Op(operator,Type(True,"bool"),Type(False,"bool"))
            self.assertEquals(test.typecheck(self.test_tbl),"bool")

        test = Bin_Op("||",Type(True,"int"),Type(False,"bool"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(getErrors()),1)


    def test_unary_op(self):

        #Test unary operators with incorrect type
        test = Unary_Op("-",Type(True,"bool"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Unary Operator - not callable with parameter bool",getErrors())

        test = Unary_Op("!",Type(3,"int"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Unary Operator ! not callable with parameter int",getErrors())

        clearErrors()
        #Test unary operators being used correctly.
        test = Unary_Op("!",Type(True,"bool"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(test.typecheck(self.test_tbl),"bool")
        self.assertEquals(len(getErrors()),0)

        test = Unary_Op("-",Type(3,"int"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(test.typecheck(self.test_tbl),"int")
        self.assertEquals(len(getErrors()),0)

        #Test uanry operator used along with binary operator
        test = Unary_Op("!", Bin_Op("&&",Type("True","bool"), Bin_Op("<", Type(3,"int") , Type(6,"int") ) ) )
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(test.typecheck(self.test_tbl),"bool")
        self.assertEquals(len(getErrors()),0)

    def test_print(self):
        test = Print(Type("test","str"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(getErrors()),0)

        test = Print( Bin_Op("+", List( [Type(4,"int"),Type(5,"int")] ) , List( [] ) ) )
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(getErrors()),0)

        #Test errors are caught within print statement
        test = Print( Bin_Op("+", List( [Type(4,"float"),Type(5,"int")] ) , List( [] ) ) )
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(getErrors()),1)

    def test_while(self):
        #Check condition is typechecked
        test_body = Return(Type(2,"int"))
        test = While(Type(4.5,"float"),test_body)
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Conditional parameter to while must be of type bool",getErrors())
        clearErrors()

        #Check errors are reported within the body
        test_body = Return(Type(2,"int"))
        test = While(Type(False,"bool"),test_body)
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(test.hasNoReturn(),False)
        self.assertIn("Return statement must be within a function",getErrors())
        clearErrors()

        #Test that variables in the body are not defined in the parent table
        test_body = Statements(InitAssign(Var(ID("v"),"bool"),Type(False,"bool")), ID("v"))
        test = While(Type(False,"bool"),test_body)
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(self.test_tbl.symbols),0)
        self.assertEquals(len(getErrors()),0)

    def test_for(self):
        #Test body errors are detected
        test_body = Return(Type(2,"int"))
        test = For(ID("a"),Type(0,"int"),Type(6,"int"),test_body)
        test.generateSymbolTable(self.test_tbl)  
        self.assertEquals(test.hasNoReturn(),False)      
        self.assertIn("Return statement must be within a function",getErrors())
        clearErrors()

        #Test that bounds are typechecked
        test_body = Statements(InitAssign(Var(ID("v"),"bool"),Type(False,"bool")), ID("v"))
        test = For(ID("a"),Type(0.0,"float"),Type(6.5,"float"),test_body)
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Start value of for loop must be of type int",getErrors())
        self.assertIn("End value of for loop must be of type int",getErrors())

    def test_if(self):
        self.test_tbl.insert("s","str","VAR")
        self.test_tbl.insert("a","bool","VAR")
    
        #Test condition is typechecked
        test = If(ID("s"),Unary_Op("!",Type(False,"bool")))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Conditional parameter to conditional must be of type bool",getErrors())
        clearErrors()

        #Test if statement works without else block
        test = If(ID("a"),Unary_Op("!",Type(False,"bool")))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(getErrors()),0)

        #Test with else statement
        test = If(ID("a"),Unary_Op("!",Type(False,"bool")),ID("s"))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(getErrors()),0)

    def test_function(self):
        #Test function with no abnormal fields
        test = Function(ID("test"),[Var(ID("num"),"int")],"int",Return(ID("num")))
        test.generateSymbolTable(self.test_tbl)
        self.assertEquals(len(getErrors()),0)

        #Test function with 2 parameters of the same name, gives an error.
        test = Function(ID("test"),[Var(ID("num"),"int"),Var(ID("num"),"int")],"int",Return(ID("num")))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Function Declaration of test: Repeated parameters in function definition of test",getErrors())
        self.assertEquals(len(getErrors()),1)
        clearErrors()

        #Test function defined within another function
        inner_function = Function(ID("inner"),[],"str",Return(Type("Hello","str")))
        test = Function(ID("test"),[Var(ID("num"),"int")],"int",Statements( inner_function, Return( ID("num") ) ) )
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Function Declaration of inner: Function can not be defined within another function",getErrors())
        clearErrors()

        #Test function can detect a non-terminal return, and detect if a return statement exists within the function body
        test = Function(ID("test"),[Var(ID("num"),"int")],"int",While(Type(False,"bool"),Return(ID("num")) ))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Function Declaration of test: Function test does not have a terminal return statement",getErrors())
        self.assertEquals(test.hasNoReturn(),False)
        clearErrors()

        #Test a function of type none, can check for return statements in the body
        test = Function(ID("test"),[Var(ID("num"),"int")],"none",Return(ID("num")))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Function Declaration of test: Function test has a return statement",getErrors())

    def test_call(self):
        test_definition = Function(ID("test"),[Var(ID("num"),"int"),Var(ID("ret"),"[int]")],"int",Return(ID("num")))
        test_definition.generateSymbolTable(self.test_tbl)

        self.test_tbl.insert("a","int","VAR")

        #Function call of non-existant function
        test = Call(ID("f"),[])
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Function f not found",getErrors())

        #Function call of a variable
        test = Call(ID("a"),[])
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Function Call of a: a is not a function",getErrors())

        #Test incorrect number of parameters is handled correctly.
        test = Call(ID("test"),[Type("param1","str")])
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Function Call of test: 2 parameters expected but 1 given",getErrors())
        clearErrors()

        #Test type mismatch is handled correctly
        test = Call(ID("test"),[Type("param1","str"),List([ID("a")])])
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Function Call of test: Type mismatch for parameter num of type int with argument of type str",getErrors())

        test = Call(ID("test"),[Unary_Op("-",Type("h","str")),List([ID("a")])])
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Function Call of test: Argument does not match type int of parameter num",getErrors())
        clearErrors()

        #Test Casting
        test = Call(ID("len"),[])
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Function Call of len: 1 parameter expected but found 0",getErrors())
        clearErrors()

        test = Call(ID("len"),[Type("argument","int")])
        self.assertEquals(test.typecheck(self.test_tbl),None)
        self.assertIn("Function Call of len: len can only be used with parameters of type list",getErrors())
        clearErrors()

        test = Call(ID("len"),[List([])])
        self.assertEquals(test.typecheck(self.test_tbl),"int")

        for cast in ["str","bool"]:
            test = Call(ID(cast),[])
            self.assertEquals(test.typecheck(self.test_tbl),None)
            self.assertIn("Function Call of "+cast+": 1 parameter expected but found 0",getErrors())
            clearErrors()

            test = Call(ID(cast),[Type(3,"int")])
            self.assertEquals(test.typecheck(self.test_tbl),cast)

        for cast in ["int","float"]:
            test = Call(ID(cast),[])
            self.assertEquals(test.typecheck(self.test_tbl),None)
            self.assertIn("Function Call of "+cast+": 1 parameter expected but found 0",getErrors())
            clearErrors()

            test = Call(ID(cast),[Type(True,"bool")])
            self.assertEquals(test.typecheck(self.test_tbl),None)
            self.assertIn("Function Call of "+cast+": "+cast+" can only be used with parameters of type int and float",getErrors())
            clearErrors()

            test = Call(ID(cast),[Type(3,"int")])
            self.assertEquals(test.typecheck(self.test_tbl),cast)

            test = Call(ID(cast),[Type(3.4,"float")])
            self.assertEquals(test.typecheck(self.test_tbl),cast)

    def test_return(self):
        #Returning different type from function type
        test_Function = Function(ID("a"),[],"bool",Return(Type(4,"int")))
        test_Function.generateSymbolTable(self.test_tbl)
        self.assertIn("Returned value of type int does not match function type bool",getErrors())
        clearErrors()

        #Return statement outside a function
        test = Return(Type("a","str"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Return statement must be within a function",getErrors())
        clearErrors()

        #Return statement with an erroneous function entry
        self.test_tbl.setFunctionEntry(("test","bool","VAR"))
        test = Return(Type("a","str"))
        test.generateSymbolTable(self.test_tbl)
        self.assertIn("Return statement must be in a function",getErrors())
        clearErrors()

    def test_statements(self):
        test_component_1 = Type("Hello","str")
        test_component_2 = Type(4,"int")
        test = Statements(test_component_1,test_component_2)

        self.assertEquals(test.statements,test_component_1)
        self.assertEquals(test.statement,test_component_2)
        self.assertEquals(test.hasTerminalReturn(),False)
        self.assertEquals(test.hasNoReturn(),True)

        #Test if return statement can be detected
        test_component_1 = Type(4,"int")
        test_component_2 = Return(Type("Hello","str"))
        test = Statements(test_component_1,test_component_2)

        self.assertEquals(test.hasTerminalReturn(),True)
        self.assertEquals(test.hasNoReturn(),False)

    def tearDown(self):
        clearErrors()

#Test the lexer of the program
class LexerTest(unittest.TestCase):

    def test_error(self):
        test = ".2.34"
        tokens = tokenize_test(test)
        self.assertIn("Lexical Error Line 1: Illegal character '.'",getErrors())

    def test_iden(self):
        test = """tmp"""
        tokens = tokenize_test(test)

        self.assertEquals(tokens[0].type,"IDEN")
        self.assertEquals(tokens[0].lineno,1)
        self.assertEquals(tokens[0].value,"tmp")

    def test_keyword(self):

        for key in keyword.keys():
            test = key
            tokens = tokenize_test(test)
            self.assertEquals(tokens[0].type,keyword[key])
            self.assertEquals(tokens[0].lineno,1)

    def test_dataType(self):
        for key in dataType.keys():
            test = key
            tokens = tokenize_test(test)
            self.assertEquals(tokens[0].type,dataType[key])
            self.assertEquals(tokens[0].lineno,1)

    def test_comma(self):
        test = ""","""
        tokens = tokenize_test(test)
        self.assertEquals(tokens[0].type,"COMMA")

    def test_colon(self):
        test = """ : """
        tokens = tokenize_test(test)
        self.assertEquals(tokens[0].type,"COL")

    def test_parentheses(self):
        test = """{ ( [  
        ] ) } """
        tokens = tokenize_test(test)
        self.assertEquals(tokens[0].value,"{")
        self.assertEquals(tokens[1].value,"(")
        self.assertEquals(tokens[2].value,"[")
        self.assertEquals(tokens[3].value,"]")
        self.assertEquals(tokens[4].value,")")
        self.assertEquals(tokens[5].value,"}")
        self.assertEquals(tokens[0].type,"L_SCOPE")
        self.assertEquals(tokens[1].type,"L_PAR")
        self.assertEquals(tokens[2].type,"L_BRACE")
        self.assertEquals(tokens[3].type,"R_BRACE")
        self.assertEquals(tokens[4].type,"R_PAR")
        self.assertEquals(tokens[5].type,"R_SCOPE")
        self.assertEquals(tokens[5].lineno,2)

    def test_type(self):
        test = """254 34.5 True "string1" 'string2' """

        tokens = tokenize_test(test)

        self.assertEquals(tokens[0].type,"INT")
        self.assertEquals(tokens[1].type,"FLOAT")
        self.assertEquals(tokens[2].type,"BOOL")
        self.assertEquals(tokens[3].type,"STRING")
        self.assertEquals(tokens[4].type,"STRING")

    def test_assignment(self):
        test = """="""

        tokens = tokenize_test(test)

        self.assertEquals(tokens[0].type,"ASSIGNMENT")

    def test_operators(self):
        test = """ <><=>===!=+-*/^%&&||!"""

        tokens = tokenize_test(test)

        self.assertEquals(tokens[0].type,"LESS")
        self.assertEquals(tokens[1].type,"GREATER")
        self.assertEquals(tokens[2].type,"LESS_EQUAL")
        self.assertEquals(tokens[3].type,"GREATER_EQUAL")
        self.assertEquals(tokens[4].type,"EQUAL")
        self.assertEquals(tokens[5].type,"NOT_EQUAL")
        self.assertEquals(tokens[6].type,"ADD")
        self.assertEquals(tokens[7].type,"SUB")
        self.assertEquals(tokens[8].type,"MUL")
        self.assertEquals(tokens[9].type,"DIV")
        self.assertEquals(tokens[10].type,"POW")
        self.assertEquals(tokens[11].type,"MOD")
        self.assertEquals(tokens[12].type,"AND")
        self.assertEquals(tokens[13].type,"OR")
        self.assertEquals(tokens[14].type,"NOT")

    def test_comment(self):
        test = """/* This is a comment  */ """
        tokens = tokenize_test(test)

        self.assertEquals(tokens,[])
        self.assertEquals(getErrors(),set())

    def tearDown(self):
        SemanticAnalyzer.clearErrors()

#Test the Parser of the program can find types of Syntax , Lexical and Runtime errors correctly.
#The parser uses all other components that have been tested above
class ParserTest(unittest.TestCase):

    def setUp(self):
        self.test_tbl = SymbolTable()

    #Test the order of precedence is parsed correctly for expressions.
    def test_mathematical_expression(self):
        test = """ 1+2/4*5"""
        nodes = comp_test(test)
        self.assertEquals(len(getErrors()),0)
        self.assertEquals(nodes.op,"+")
        self.assertEquals(nodes.rhs.op,"*")
        self.assertEquals(nodes.rhs.lhs.op,"/")

    def test_lexical_error(self):
        test = """2.3443.454a
        ;$@
        """
        comp_test(test)

        self.assertIn("Lexical Error Line 1: Illegal character '.'",getErrors())
        self.assertIn("Lexical Error Line 2: Illegal character '@'",getErrors())
        self.assertIn("Lexical Error Line 2: Illegal character '$'",getErrors())
        self.assertIn("Lexical Error Line 2: Illegal character ';'",getErrors())

    def test_syntax_error(self):
        test = """/*This is a
        comment */
        print)"Hello World"(
        """
        comp_test(test)
        self.assertIn("Line 3:Syntax Error at )",getErrors())

    def test_index_out_of_bounds(self):
        test = """[][0]"""
        comp_test(test)
        self.assertIn("Runtime Error : Index out of bounds.",getErrors())

    def test_zero_division(self):
        test = """(5+4+8*7) / 0"""
        comp_test(test)
        self.assertIn("Runtime Error : Can not divide by 0.",getErrors())

    def test_recursion(self):
        test = """
        def factorial(x : int) : int {
            if x<=0{
                return 1
            }
            else{
                return x * factorial(x-1)
            }
        }
        if factorial(3)==6 {
            print("test_recursion_successful")
        }
        """
        comp_test(test)
        self.assertEquals(len(getErrors()),0)

    def test_runtime_exception(self):
        test = """
        def infinite_recursion(foo : int) : int {
            return infinite_recursion(foo + 1)
        }

        infinite_recursion(0)
        """
        comp_test(test)
        self.assertIn("Runtime Error : Runtime exception found.",getErrors())

    def tearDown(self):
        clearErrors()


if __name__=="__main__":
    unittest.main()