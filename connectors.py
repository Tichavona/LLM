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
import pyodbc as db
from sqlalchemy import create_engine as ce
from sqlalchemy.exc import SQLAlchemyError as sqlError
from dotenv import load_dotenv as ld
import os

class DBConnector:
    def __init__(self, driver, server, dbase, user, pwd):
        ld()
        
        # Server options
        self.server = os.getenv(server)

        # User credentials options
        self.user = os.getenv(user)
        self.pwd = os.getenv(pwd)

        # Database options
        self.dbase = os.getenv(dbase)
        
        # Driver options
        self.driver = driver

    def pyodbcConnection(self):
                
        try:
            conn_str = f"""DRIVER={self.driver};
                            SERVER={self.server};
                            DATABASE={self.dbase};
                            UID={self.user};
                            PWD={self.pwd};
                            Trusted_Connection=No;"""
            conn = db.connect(conn_str)
            print("Connected to database successfully!")
            return conn
        except Exception as e:
            print("Error connecting to database:", str(e))
            return None
        
    def alchemyConnection(self):
        self.driver = self.driver[1:-1]        
        try:
            dbaseURL = f"mssql+pyodbc://{self.user}:{self.pwd}@{self.server}/{self.dbase}?driver={self.driver}"
            engine = ce(dbaseURL)
            connection = engine.connect()
            if connection:
                print("Connected to database successfully!")
            return engine
        except sqlError as e:
            print("Error connecting to database:", str(e))
            return None

        






