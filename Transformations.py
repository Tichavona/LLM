#!/usr/bin/env python
# coding: utf-8
# Tichavona Vakisai
# Senior Data Scientist
# Deep Analytics
# tich@deepanalytics.ml
# +263 71 379 1914
# Version 1.0
# 29/03/2024 18:18

import pandas as pd
from datetime import datetime
import re

class Transformations():
    def __init__(self, df, col = None, colName=None):
        self.df = df
        self.colName = colName or "ACCOUNTNUMBER"
        if isinstance(col, list):
            self.colList = col
        else:
            self.col = col
        self.pattern = re.compile(r'\b(CINDERELLA B MINE|CORNER STONE SCHOOL|KAZMART INCORPORATED P/L|LEEJAY ENTERPRISES P/L|FARMAK PRE SCHOOL)\b')

    def dateTrans(self):
        # Convert integer_dates to string and pad with leading zeros
        self.df[self.col] = self.df[self.col].apply(lambda x: x+19000000).astype(str)

        # Extract year, month, and day parts from the string
        self.df['year'] = self.df[self.col].apply(lambda x: int(str(x)[:4]) if str(x) != 'nan' else '1900')
        self.df['month'] = self.df[self.col].apply(lambda x: int(str(x)[4:6]) if str(x) != 'nan' else '00')
        self.df['day'] = self.df[self.col].apply(lambda x: int(str(x)[6:8]) if str(x) != 'nan' else '00')

        # Handle situation where date is represented by 0
        self.df.loc[self.df[self.col] == '19000000', [self.col, 'year', 'month', 'day']] = pd.NaT, 0, 0, 0

        # Convert to datetime
        self.df[self.col] = pd.to_datetime(self.df[['year', 'month', 'day']], errors='coerce').dt.date

        # Drop intermediate columns
        self.df.drop(columns=['year', 'month', 'day'], inplace=True)
        return self.df
    
    # Function to combine values from specified columns
    def combine_columns(self, row):
        return ''.join(str(row[col]) for col in self.colList)
    
    def newColumn(self):
        # Apply the function to create the new column
        self.df[self.colName] = self.df.apply(self.combine_columns, axis=1)
        return self.df
    
    def accountNumber(self):
        # Apply the function to create the new column
        self.df.insert(0, self.colName, self.df.apply(self.combine_columns, axis=1))
        return self.df
    
    def balanceConversion(self):
        self.df[self.col] = self.df[self.col].apply(lambda x: round(x/100, 2))
        return self.df
    
    def additionalColumns(self):
        self.df["SYSTEM"] = 'EQUATION'
        self.df["ENTITY"] = 'ZBBL'
        self.df["CLUSTER"] = 'BANKING'
        self.df["DATEMODIFIED"] = datetime.now().date() #pd.to_datetime(datetime.now().date().strftime("%Y-%m-%d")).dt.date
        return self.df

    def getIndexValues(self, x, index):
        if len(x.split(",")) > 1:
            return x.split(",")[index].strip()
        elif len(x.split("  ")) > 1:
            return x.split("         ")[index].strip()
        elif re.search(self.pattern, str(x)):
            return x       
    
    def columnSplitByComma(self):
        self.df[self.colList[0]] = self.df[self.colList[2]].astype(str).apply(lambda x: self.getIndexValues(x, 0))
        self.df[self.colList[1]] = self.df[self.colList[2]].astype(str).apply(lambda x: self.getIndexValues(x, 1))
        return self.df
    
    def titlesTrans(self):
        titles = {'(MS)':'MS', '(MRS)':'MRS', 'ESTIMATION.J.MR':'MR', 'S.MR':'MR', 'C.MR':'MR', 'T.MISS':'MISS', 
                  '(JNR)MR':'MR', 'J.MR&MRS':'MR & MRS', 'ZULU)MRS':'MRS', 'MR&M':'MR & MRS', '(MR)':'MR', 
                  'MRS`':'MRS', 'MR.':'MR', 'DR.':'DR', '.MR':'MR', 'M.MR':'MR', 'B.MR':'MR', '\MISS\\':'MISS',
                  'MR':'MR', 'MRS':'MRS', 'MISS':'MISS', 'MS':'MS', 'DR':'DR', 'PROF':'PROF', 'REV':'REV',
                  'DOCTOR':'DOCTOR', 'PROFESSOR':'PROFESSOR', 'REVEREND':'REVEREND', 'ADV':'ADV', 
                  'ADVOCATE':'ADVOCATE', 'COM':'COM', 'COMMISSIONER':'COMMISSIONER', 'SGT':'SGT', 
                  'SERGENT':'SERGENT', 'ENG':'ENG', 'ENGINEER':'ENGINEER', 'HON':'HON', 'NS':'MS'}

        self.df['TITLE'] = self.df['CUSTOMERSHORTNAME'].astype(str).apply(
            lambda x: titles[x.split()[-1]]
            if (len(x)>0 and x.split()[-1] in titles.keys())
            else ''
            )
        return self.df
    
    def nameTrans(self):
        names = {'(MS)':'', '(MRS)':'', 'ESTIMATION.J.MR':'ESTIMATION J.', 'S.MR':'S.', 'C.MR':'C.', 'T.MISS':'T.',
                 '(JNR)MR':'JNR', 'J.MR&MRS':'J.', 'ZULU)MRS':'ZULU', 'MR&M':'', '(MR)':'', 'MRS`':'', 'MR.':'',
                 'DR.':'', '.MR':'', 'M.MR':'M.', 'B.MR':'B.', '\MISS\\':'', 'MR':'', 'MRS':'', 'MISS':'', 'MS':'',
                 'DR':'', 'PROF':'', 'REV':'', 'DOCTOR':'', 'PROFESSOR':'', 'REVEREND':'', 'ADV':'', 'ADVOCATE':'',
                 'COM':'', 'COMMISSIONER':'', 'SGT':'', 'SERGENT':'',  'ENG':'', 'ENGINEER':'', 'HON':'', 'NS':''}

        self.df['CUSTOMERSHORTNAME'] = self.df['CUSTOMERSHORTNAME'].astype(str).apply(
            lambda x: (" ".join(str(x).split()[:-1])+' '+names[x.split()[-1]]).strip()
            if len(str(x))>2 and str(x).split()[-1] in names.keys()
            else x
            )
        self.df.rename(columns = {'CUSTOMERSHORTNAME':'CUSTOMERNAME'}, inplace = True)
        return self.df
    
    def colSCPF(self):
        self.df["SCBALANCE"] = self.df[self.col].sum()*-1
        return self.df
    
    def filterSCPF(self):
        self.df = self.df.loc[self.df[self.col] == 'N'][["BRANCHCODE", "CUSTOMERNUMBER", "SUFFIX", "DATEOPENED", "DATECLOSED", "ACCOUNTBALANCE",
                       "CURRENCY", "ACCOUNTNAME", "EMPLOYERCODE", "BLOCKED", "INACTIVE", "DORMANT", "ACCOUNTOFFICER",
                        "SCODL", "SCACD", "SCACT", "SCCTP", "SCP1R"]]
        return self.df
    
