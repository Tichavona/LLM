from readAndLoad import DatabaseReader as dbReader
from Transformations import Transformations
from readAndLoad import csvReader

class GFPF():

    def __init__(self, opssys, connectorType, server, dbase, user, pwd):
        self.opssys = opssys
        self.connectorType = connectorType
        self.server = server
        self.dbase = dbase
        self.user = user
        self.pwd = pwd

    def gfpfTransformation(self):
        reader = dbReader(self.opssys, self.connectorType, self.server, self.dbase, self.user, self.pwd)
        # reader = csvReader(r"C:\Users\ACER\Downloads\ZB Customer Extract 2.csv")
        
        # Define table name and columns to read
        table_name = "EQ4_GFPF"
        columns = ["GFCUS", "GFCUN", "GFCRF", "GFCOD", "GFDLM", "GFBRNM", "GFSTMP", "GFCREF", "GFPSTM", "GFNSTM"]        
        newColNames = ["CUSTOMERNUMBER", "CUSTOMERSHORTNAME", "IDNUMBER", "DATEOPENED", "DATE2", "BRANCHCODE", "GFSTMP", "GFCREF", "GFPSTM", "GFNSTM"]
        
        # Call read_table method to retrieve data
        data = reader.read_table(table_name, columns, newColNames)
        # data = reader.readCSV()
        for col in ["DATEOPENED", "DATE2", "GFPSTM", "GFNSTM"]: 
            Transformer = Transformations(data, col)
            data = Transformer.dateTrans()
        Transformer = Transformations(data)
        data = Transformer.titlesTrans()
        data = Transformer.nameTrans()
        data = Transformer.additionalColumns()
        return data
    
    