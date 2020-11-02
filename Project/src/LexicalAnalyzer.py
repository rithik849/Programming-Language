
delimiters = [",",":",';']
math_op = ['*','/','+','-','^','%']
comp_op = ["<",">","<=",">=","==","!="]
bool_op = ["&&","||","!"]
assignment = ["="]
types = ["int","float","str","bool","none"]
keywords = ["if","else","while","do","for","new","var","val","to"]
parentheses = ["(",")","[","]","{","}"]
digit = list("0123456789")
bool_val = ["True","False"]

#Responsible for tokenizing a program file
class LexicalAnalyzer:

    def __init__(self,filename):
        # Stores tokens
        self.tokens = []
        #Used for multi-line comments
        self.comment = False
        #Stores a list of errors
        self.errors  = []

        lines = []
        row = 0
        with open(filename,"r") as file:
            lines = file.readlines()
        
        for line in lines:
            row +=1
            i = 0
            s = line
            while (i<len(line)):
                # print(i)
                # print("s:\""+s[i]+"\"")
                # print("Length:"+str(len(line)))
                #Produce tokens for the file
                if ((s[i:i+2] == "/*") or (self.comment)):
                    i = self.skip_com(s,i)
                elif (s[i] in [" ","\n","\t","\r"]):
                    i = self.skip_ws(s,i)
                elif (s[i].isalpha()):
                    i = self.find_keyword_or_id(s,i)
                elif ((s[i:i+2] in comp_op) or (s[i] in comp_op)):
                    i = self.find_comp_op(s,i)
                elif (s[i] in assignment):
                    i = self.find_assignment(s,i)
                elif (s[i] in math_op):
                    i = self.find_math_op(s,i)
                elif ((s[i:i+2] in bool_op) or (s[i] in bool_op)):
                    i = self.find_bool_op(s,i)
                elif (s[i] in parentheses):
                    i = self.find_parentheses(s,i)
                elif (s[i] in digit):
                    i = self.find_num(s,i)
                elif (s[i]=="\""):
                    tmp = self.find_string(s,i)
                    #If none is returned, indicates the last string quotation was not found
                    if (tmp != None):
                        i = tmp
                    else:
                        #Gives location of first quotation mark within the error
                        self.errors.append(
                            "End string quotation not found for start quotation:"+
                            " row:"+str(row)+" column:"+str(i)
                            )
                        break
                elif (s[i] in delimiters):
                    i = self.find_delimiter(s,i)
                else:
                    self.errors.append("Unknown Character:"+"\""+s[i]+"\"")
                    break

        if (self.errors):
            self.printErrors()
        print("Result:")
        #print(self.tokens)
        for token in self.tokens:
            print(token)

        print(filter(lambda a : a[0]=="PAR",self.tokens))

    def printErrors(self):
        print("Errors:")
        for error in self.errors:
            print(error)

    #Find delimiters
    def find_delimiter(self,s,i):
        m = {",":"COMMA",":":"COL",";":"SEMI_COL"}
        if (s[i] in delimiters):
            self.tokens.append( (m[s[i]],s[i]) )
            i+=1
        return i

    #Find numbers
    def find_num(self,s,i):
        if (s[i] in digit):
            start = i
            i+=1
            while (s[i] in (digit+["."])):
                i += 1
            self.tokens.append( ("LITERAL",s[start:i]) )
        return i

    #Finds a variable that searches for an assignment
    def find_assignment(self,s,i):
        if (s[i] in assignment):
            self.tokens.append( ("ASSIGNMENT",s[i]) )
            i += 1
        return i

    #Finds mathematical operators
    def find_math_op(self,s,i):
        if (s[i] in math_op):
            self.tokens.append( ("MATH_OP",s[i]) )
            i += 1
        return i

    # Finds comparison operators
    def find_comp_op(self,s,i):
        if (s[i:i+2] in comp_op):
            self.tokens.append( ("COMP_OP",s[i:i+2]) )
            i += 2
        elif (s[i] in comp_op):
            self.tokens.append(("COMP_OP",s[i]))
            i += 1
        return i

    # Finds boolean operators
    def find_bool_op(self,s,i):
        if (s[i:i+2] in bool_op):
            self.tokens.append(("BOOL_OP",s[i:i+2]))
            i += 2
        elif (s[i] in bool_op):
            self.tokens.append( ("BOOL_OP",s[i]) )
            i += 1
        return i

    #Finds strings
    def find_string(self,s,i):
        if (s[i]=="\""):
            start = i
            i += 1
            while (i<len(s) and s[i]!="\""):
                i += 1
            #If we do not find the closing double quotation mark we return None
            if (i>=len(s)):
                return None
            self.tokens.append( ("LITERAL",s[start:i+1]) )
            return i+1

    #Identifies tokens as parentheses
    def find_parentheses(self,s,i):
        par = {"(":"L_PAR",")":"R_PAR","{":"L_SCOPE_PAR","}" : "R_SCOPE_PAR","[" : "L_LIST_PAR" , "]" : "R_LIST_PAR"}
        if (s[i] in parentheses):
            self.tokens.append((par[s[i]],s[i]))
            i += 1
        return i

    #Finds potential keywords and identifiers
    def find_keyword_or_id(self,s,i):
        word =""
        if (s[i].isalpha()):
            first_character_id = i
            while ((i < len(s)) and (s[i].isalpha() or s[i].isdigit() or (s[i]=="_"))):
                i += 1
            if (i >= len(s)):
                word = s[first_character_id:]
                return i

            if s[i] in (delimiters+math_op+comp_op+parentheses+assignment+[" "]):
                word = s[first_character_id:i]

            if (word in keywords):
                self.tokens.append( (word.upper(),word) )
            elif (word in bool_val):
                self.tokens.append( ("LITERAL",word) )
            elif (word in types):
                self.tokens.append( ("TYPE",word) )
            else:
                self.tokens.append( ("IDEN",word) )

        return i

    #Skips white spaces
    def skip_ws(self,s,i):
        if (s[i]==" "):
            i += 1
        elif (s[i] in [" ","\n","\t","\r"]):
            i = i+1
        return i

    #Skips comments
    def skip_com(self,s,i):
        if (s[i:i+2]=="/*"):
            self.comment = True
        if (self.comment):
            #If we do not find the end comment we set i to the end of the line
            end_index = s.find("*/")
            if (end_index == -1):
                i = len(s)
            else:
                self.comment = False
                i = end_index+2
        return i

LexicalAnalyzer("testfile.txt")
