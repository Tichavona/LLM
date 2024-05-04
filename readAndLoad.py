#!/usr/bin/env python
# coding: utf-8
# Tichavona Vakisai
# Senior Data Scientist
# Deep Analytics
# tich@deepanalytics.ml
# +263 71 379 1914
# Version 1.0
# 29/03/2024 18:18


# Importations
import streamlit as st
from connectors import DBConnector
from sqlalchemy import MetaData as md
from sqlalchemy.exc import SQLAlchemyError as sqlError
import pandas as pd

class csvReader:
    def __init__(self, url):
        self.url = url

    def readCSV(self):
        data = pd.read_csv(self.url, low_memory=False)
        data["BRANCHCODE"] = data["BRANCHCODE"].astype(str).apply(lambda x : str(x).zfill(4))
        accNumber = []
        for i in data["CUSTOMERNUMBER"]:
            if len(str(i).split('.')[0]) < 6:
                accNumber.append(str(i).split('.')[0].zfill(6))
            elif len(str(i).split('.')[0]) > 6:#in ['2024-04-19 10:54:50.725', '2024-04-19 10:57:52.440', '2024-04-19 10:59:58.236', 
                            #'2024-04-19 11:00:56.228', '2024-04-19 11:01:53.093', '2024-04-19 11:05:12.806']:
                accNumber.append('000000')            
            else:
                accNumber.append(str(i).split('.')[0])
        data["CUSTOMERNUMBER"] = accNumber
        data["SUFFIX"] = data["SUFFIX"].astype(str).apply(lambda x : str(x).zfill(3))
        return data

class DatabaseReader:
    def __init__(self, opssys, connectorType, server, dbase, user, pwd):
        self.connectorType, self.server, self.dbase, self.user, self.pwd = connectorType,server, dbase, user, pwd
        self.opssys = opssys
                
    def read_table(self, table_name, columns, newColNames):
        """
        Reads data from a specific table with given columns.
        
        Args:
            table_name (str): Name of the table to read from.
            columns (list of str): List of columns to retrieve.
        
        Returns:
            pandas DataFrame containing the data from the specified table and columns.
        """
        server, dbase, user, pwd = "SERVER", "SOURCEBASE", "USER", "PWORD"
        # Establish connection
        if self.opssys == "Linux":
            driver = "{ODBC Driver 17 for SQL Server}"
            self.db_connector = DBConnector(driver, server, dbase, user, pwd)
            if self.connectorType == "pyodbc":
                conn = self.db_connector.pyodbcConnection()
                if conn:
                    try:
                        # Construct SQL query
                        columns_str = ', '.join(columns)
                        query = f"SELECT {columns_str} FROM {table_name};"
                        
                        # Execute query and fetch data
                        data = pd.read_sql(query, conn)
                        data.columns = newColNames
                        return data
                    except Exception as e:
                        print("Error reading data:", str(e))
                    finally:
                        conn.close()
            elif self.connectorType == "sqlalchemy":
                conn = self.db_connector.alchemyConnection()        
                if conn:
                    try:
                        # Construct SQL query
                        columns_str = ', '.join(columns)
                        query = f"SELECT {columns_str} FROM {table_name};"
                        
                        # Execute query and fetch data
                        data = pd.read_sql(query, conn)
                        data.columns = newColNames
                        return data
                    except sqlError as e:
                        print("Error reading data:", str(e))
                        
        elif self.opssys == "Windows":
            self.driver = "{SQL Server}"
            self.db_connector = DBConnector(driver, server, dbase, user, pwd)
            if self.connectorType == "pyodbc":
                conn = self.db_connector.pyodbcConnection()
                print(conn)
                if conn:
                    try:
                        # Construct SQL query
                        columns_str = ', '.join(columns)
                        query = f"SELECT {columns_str} FROM {table_name};"
                        
                        # Execute query and fetch data
                        data = pd.read_sql(query, conn)
                        data.columns = newColNames
                        return data
                    except Exception as e:
                        print("Error reading data:", str(e))
                    finally:
                        conn.close()
            elif self.connectorType == "sqlalchemy":
                conn = self.db_connector.alchemyConnection()
                print(conn)        
                if conn:
                    try: 
                        # Construct SQL query
                        columns_str = ', '.join(columns)
                        query = f"SELECT {columns_str} FROM {table_name};"
                        
                        # Execute query and fetch data
                        data = pd.read_sql(query, conn)
                        data.columns = newColNames
                        return data
                    except sqlError as e:
                        print("Error reading data:", str(e))

    