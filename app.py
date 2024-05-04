#!/usr/bin/env python
# coding: utf-8
# Tichavona Vakisai
# Senior Data Scientist
# Deep Analytics
# tich@deepanalytics.ml
# +263 71 379 1914
# Version 1.0
# 29/03/2024 18:18

import streamlit as st
from sqlalchemy import MetaData as md, Table as tbl, select, inspect
from sqlalchemy.exc import SQLAlchemyError as sqlError
from sqlalchemy.orm import sessionmaker as sm
from sqlalchemy.ext.declarative import declarative_base as dbse
from sqlalchemy import Column, Integer, String
# from passlib.hash import pbkdf2_sha256
from scpf import SCPF
from aazpf import AAZPF
from c4pf import C4PF
from c5pf import C5PF
from c6pf import C6PF
from ctpf import CTPF
from gfpf import GFPF
from gppf import GPPF
from bgpf import BGPF
from dLoan import dLoan as dl
from branchCodes import bCodes

def main():
    # Add Streamlit UI
    st.title("Extract Preview")

    with st.sidebar:
        st.sidebar.title("Source Database")
        server = st.text_input("Enter Server")
        dbase = st.text_input("Enter Database", value="master")
        user = st.text_input("Enter User")
        pwd = st.text_input("Enter Password", type="password")
        connectorType = st.selectbox("Select Connector", ["pyodbc", "sqlalchemy"])
        opssys = st.selectbox("Select Operating System", ["Linux", "Windows"])
        btnProcess = st.button("Enter/Process")
    
    # Create an instance of DatabaseReader based on the selected connector
    if btnProcess:
        scpfTransformer = SCPF(opssys, connectorType, server, dbase, user, pwd)
        scpf = scpfTransformer.scpfTransformation()
        st.write('Table SCPF')
        st.dataframe(scpf.head()) 

        aazpfTransformer = AAZPF(opssys, connectorType, server, dbase, user, pwd)
        aazpf = aazpfTransformer.aazpfTransformation()
        st.write('Table AAZPF')
        st.dataframe(aazpf.head())

        c4pfTransformer = C4PF(opssys, connectorType, server, dbase, user, pwd)
        c4pf = c4pfTransformer.c4pfTransformation()
        st.write('Table C4PF')
        st.dataframe(c4pf.head())

        c5pfTransformer = C5PF(opssys, connectorType, server, dbase, user, pwd)
        c5pf = c5pfTransformer.c5pfTransformation()
        st.write('Table C5PF')
        st.dataframe(c5pf.head())

        c6pfTransformer = C6PF(opssys, connectorType, server, dbase, user, pwd)
        c6pf = c6pfTransformer.c6pfTransformation()
        st.write('Table C6PF')
        st.dataframe(c6pf.head())

        ctpfTransformer = CTPF(opssys, connectorType, server, dbase, user, pwd)
        ctpf = ctpfTransformer.ctpfTransformation()
        st.dataframe(ctpf.head())

        gfpfTransformer = GFPF(opssys, connectorType, server, dbase, user, pwd)
        gfpf = gfpfTransformer.gfpfTransformation()
        st.write('Table GFPF')
        st.dataframe(gfpf.head())

        gppfTransformer = GPPF(opssys, connectorType, server, dbase, user, pwd)
        gppf = gppfTransformer.gppfTransformation()
        st.write('Table GPPF')
        st.dataframe(gppf.head())

        dLoanTransformer = dl(opssys, connectorType, server, dbase, user, pwd)
        dLoan = dLoanTransformer.dLoanTransformation()
        st.dataframe(dLoan.head())

        bgpfTransformer = BGPF(opssys, connectorType, server, dbase, user, pwd)
        bgpf = bgpfTransformer.bgpfTransformation()
        st.write('Table BGPF')
        st.dataframe(bgpf.head())       
        
        # bCodesTransformer = bCodes(opssys, connectorType, server, dbase, user, pwd)
        # branchCodes = bCodesTransformer.bCodesTransformation()
        # st.dataframe(branchCodes.head())

# Example usage:
if __name__ == "__main__":
    main()

