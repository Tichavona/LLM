from readAndLoad import DatabaseReader as dbReader, csvReader
from Transformations import Transformations

class GPPF():

    def __init__(self, opssys, connectorType, server, dbase, user, pwd):
        self.opssys = opssys
        self.connectorType = connectorType
        self.server = server
        self.dbase = dbase
        self.user = user
        self.pwd = pwd

    def gppfTransformation(self):
        reader = dbReader(self.opssys, self.connectorType, self.server, self.dbase, self.user, self.pwd)
        # reader = csvReader(r"C:\Users\ACER\Downloads\ZB Customer Extract 2.csv")
        
        # Define table name and columns to read
        table_name = "EQ4_GPPF"
        columns = ["GPP1R", "GPP1D"]        
        newColNames = ["GPP1R", "CLIENTQUALITY"]
        
        # Call read_table method to retrieve data
        data = reader.read_table(table_name, columns, newColNames)
        # data = reader.readCSV()
        col = ['CLIENTQUALITYCODE', 'CLIENTQUALITYDESCRIPTION', 'CLIENTQUALITY']
        Transformer = Transformations(data, col)
        data = Transformer.columnSplitByComma()
        data = Transformer.additionalColumns()
        return data
    
    