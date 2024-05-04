from readAndLoad import DatabaseReader as dbReader, csvReader
from Transformations import Transformations


class SCPF():

    def __init__(self, opssys, connectorType, server, dbase, user, pwd):
        self.opssys = opssys
        self.connectorType = connectorType
        self.server = server
        self.dbase = dbase
        self.user = user
        self.pwd = pwd

    def scpfTransformation(self):
        reader = dbReader(self.opssys, self.connectorType, self.server, self.dbase, self.user, self.pwd)
        # reader = csvReader(r"C:\Users\ACER\Downloads\ZB Customer Extract 2.csv")
        
        # Define table name and columns to read
        table_name = "EQ4_SCPF"
        columns = ["SCAB", "SCAN", "SCAS", "SCOAD", "SCCAD", "SCBAL", "SCCCY", "SCSHN", "SCP5R",
                    "SCAI17", "SCAI20", "SCAI90", "SCACO", "SCODL", "SCACD", "SCACT", "SCCTP", "SCP1R", "SCAI14"]        
        newColNames = ["BRANCHCODE", "CUSTOMERNUMBER", "SUFFIX", "DATEOPENED", "DATECLOSED", "ACCOUNTBALANCE",
                       "CURRENCY", "ACCOUNTNAME", "EMPLOYERCODE", "BLOCKED", "INACTIVE", "DORMANT", "ACCOUNTOFFICER",
                        "SCODL", "SCACD", "SCACT", "SCCTP", "SCP1R", "SCAI14"]
        
        # Call read_table method to retrieve data
        data = reader.read_table(table_name, columns, newColNames)
        # data = reader.readCSV()
        col = "SCAI14"
        Transformer = Transformations(data, col)
        data = Transformer.filterSCPF()
        for col in ["DATEOPENED", "DATECLOSED", "ACCOUNTBALANCE"]: 
            Transformer = Transformations(data, col)
            if col == "ACCOUNTBALANCE":
                data = Transformer.balanceConversion()
                data = Transformer.colSCPF()
            else:
                data = Transformer.dateTrans()
        col, colName = ["BRANCHCODE", "CUSTOMERNUMBER", "SUFFIX"], "ACCOUNTNUMBER"
        Transformer = Transformations(data, col, colName)
        data = Transformer.accountNumber()
        data = Transformer.additionalColumns()
        return data
    
    