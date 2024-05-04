from readAndLoad import DatabaseReader as dbReader
from Transformations import Transformations
from readAndLoad import csvReader

class AAZPF():

    def __init__(self, opssys, connectorType, server, dbase, user, pwd):
        self.opssys = opssys
        self.connectorType = connectorType
        self.server = server
        self.dbase = dbase
        self.user = user
        self.pwd = pwd

    def aazpfTransformation(self):
        reader = dbReader(self.opssys, self.connectorType, self.server, self.dbase, self.user, self.pwd)
        # reader = csvReader(r"C:\Users\ACER\Downloads\ZB Customer Extract 2.csv")
        
        # Define table name and columns to read
        table_name = "EQ4_AAZPF"
        columns = ["AAZCUS", "AAZMPHN", "AAZHPHN", "AAZBPHN", "AAZBDTE", "AAZCLC", "AAZPLC", "AAZNODP", "AAZIDC", 
                   "AAZIDN", "AAZIDIP", "AAZSAL", "AAZSCCY"]        
        newColNames = ["CUSTOMERNUMBER", "MOBILEPHONE", "HOMEPHONE", "BUSINESSPHONE", "DOB", "CUSTOMERLOCATION",
                       "CUSTOMERLOCATION2", "NUMBEROFDEPENDENTS", "IDCERTIFICATE", "IDNUMBER", "PLACE",
                       "SALARYAMOUNT", "SALARYCURRENCY"]
        
        # Call read_table method to retrieve data
        data = reader.read_table(table_name, columns, newColNames)
        # data = reader.readCSV()
        for col in ["DOB"]: 
            Transformer = Transformations(data, col)
            data = Transformer.dateTrans()
            data = Transformer.additionalColumns()
        return data
    
    