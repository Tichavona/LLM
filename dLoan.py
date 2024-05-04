from readAndLoad import DatabaseReader as dbReader
from Transformations import Transformations

class dLoan():

    def __init__(self, opssys, connectorType, server, dbase, user, pwd):
        self.opssys = opssys
        self.connectorType = connectorType
        self.server = server
        self.dbase = dbase
        self.user = user
        self.pwd = pwd

    def dLoanTransformation(self):
        reader = dbReader(self.opssys, self.connectorType, self.server, self.dbase, self.user, self.pwd)
        
        # Define table name and columns to read
        table_name = "EQ4_DepositLoan"
        columns = ["DCODE", "DESCRIPTION"]        
        newColNames = ["ATCODE", "DESCRIPTION"]
        
        # Call read_table method to retrieve data
        data = reader.read_table(table_name, columns, newColNames)
        Transformer = Transformations(data)
        data = Transformer.additionalColumns()
        return data