from readAndLoad import DatabaseReader as dbReader
from Transformations import Transformations
from readAndLoad import csvReader

class C4PF():

    def __init__(self, opssys, connectorType, server, dbase, user, pwd):
        self.opssys = opssys
        self.connectorType = connectorType
        self.server = server
        self.dbase = dbase
        self.user = user
        self.pwd = pwd

    def c4pfTransformation(self):
        reader = dbReader(self.opssys, self.connectorType, self.server, self.dbase, self.user, self.pwd)
        # reader = csvReader(r"C:\Users\ACER\Downloads\ZB Customer Extract 2.csv")
        
        # Define table name and columns to read
        table_name = "EQ4_C4PF"
        columns = ["C4CTP", "C4CTD"]        
        newColNames = ["C4CTP", "CUSTOMERTYPE"]
        
        # Call read_table method to retrieve data
        data = reader.read_table(table_name, columns, newColNames)
        # data = reader.readCSV()
        Transformer = Transformations(data)
        data = Transformer.additionalColumns()
        return data
    
    