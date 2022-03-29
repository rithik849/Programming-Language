class SymbolTable:

    def __init__(self,parentTable = None , functionRecord= None):
        self.functionRecord = functionRecord
        self.parentTable = parentTable
        self.symbols = []

    #Set the function record
    def setFunctionEntry(self,functionRecord):
        self.functionRecord = functionRecord

    #Get the function record
    def getFunctionEntry(self):
        return self.functionRecord

    #Prints the records of the table
    def printTable(self):
        for token in self.symbols:
            print(token)

    #Finds the root table. i.e. the global table
    def getRoot(self):
        parent = self
        while parent.parentTable:
            parent = parent.parentTable
        return parent

    #Clear the table fields
    def clear(self):
        self.parentTable = None
        self.symbols = []
        self.functionRecord = None

    #Get the parent table
    def getParent(self):
        return self.parentTable

    #Clone the symbol table state.
    def setSymbolTable(self,table):
        self.parentTable = table.parentTable
        self.symbols = table.symbols
        self.functionRecord = table.functionRecord

    #insert identifier information into the symbol table
    def insert(self,identifier,dataType,idenType,localTable=None,parameters = []):
        check = [i for i in self.symbols if i[0]==identifier]
        
        if check:
            self.symbols.remove(check[0])

        self.symbols.append((identifier,dataType,idenType,localTable,parameters))
        return True

    #Search for an identifier in the current table scope and those of its ancestors.
    def lookup(self,identifier):
        for record in self.symbols:
            if (record[0]==identifier):
                return record

        if (self.parentTable):
            return self.parentTable.lookup(identifier)
        else:
            return None

    def __repr__(self):
        return "\n"+str(self.symbols)+"\n"