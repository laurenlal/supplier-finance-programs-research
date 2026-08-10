# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from pandasql import sqldf
from openpyxl import load_workbook
from openpyxl.styles import numbers
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import calcbench as cb
import re

# %%
df = pd.read_csv('data/py_users.csv')

# %%
df['user?'] = (
    df["SupplierFinanceProgramObligation"].notnull() |
    df["SupplierFinanceProgramObligationIncrease"].notnull() |
    df["SupplierFinanceProgramObligationSettlement"].notnull()
).astype(int)

#filter time for PY
df["fiscal_period"] = pd.to_datetime(df["FiscalYearEndDate"], errors="coerce")
cutoff = pd.Timestamp("2022-12-15")
df["eligible"] = df["fiscal_period"] > cutoff

#grab data before the 2nd cutoff date 
cutoff2 = pd.Timestamp("2024-12-14")
df["eligible2"] = df["fiscal_period"] > cutoff2

df = df[df["eligible"] == True ]
df = df[df["eligible2"] == False ]
df = df[df["calendar_period"] == 0]
df = df.drop(columns=["eligible", "eligible2"])

#OG DATAAAA
df_og = pd.read_csv('data/original.csv')

df_og['user?'] = (
    df_og["SupplierFinanceProgramObligation"].notnull() |
    df_og["SupplierFinanceProgramObligationIncrease"].notnull() |
    df_og["SupplierFinanceProgramObligationSettlement"].notnull()
).astype(int)

#filter time for CY
df_og["fiscal_period"] = pd.to_datetime(df_og["FiscalYearEndDate"], errors="coerce")
cutoff = pd.Timestamp("2023-12-15")
df_og["eligible"] = df_og["fiscal_period"] > cutoff

        #grab data before the 2nd cutoff date 
cutoff2 = pd.Timestamp("2025-12-14")
df_og["eligible2"] = df_og["fiscal_period"] > cutoff2

df_og = df_og[df_og["eligible"] == True ]
df_og = df_og[df_og["eligible2"] == False ]
df_og = df_og[df_og["calendar_period"] == 0]
df_og = df_og.drop(columns=["eligible", "eligible2"])


#-------------
py_tickers = df.loc[df["user?"] == 1, "ticker"].unique()
cy_tickers = df_og.loc[df_og["user?"] == 1, "ticker"].unique()

#len of py_tickers: 195
#len of cy_tickers: 224

# (29 new companies)


#Missing from PY: 
# ['ARCO',
#  'ATR',
#  'BALL',
#  'BALY',
#  'BKR',
#  'CAL',
#  'CHTR',
#  'CMPR',
#  'COHR',
#  'COLM',
#  'CPRI',
#  'CWH',
#  'CYH',
#  'DELL',
#  'ESLT',
#  'FIVE',
#  'FMC',
#  'FOXF',
#  'FYBR',
#  'GEV',
#  'GIS',
#  'GT',
#  'HAL',
#  'HON',
#  'INGM',
#  'ITT',
#  'KR',
#  'KSS',
#  'KTB',
#  'LEG',
#  'MAMO',
#  'MDT',
#  'MELI',
#  'ORLY',
#  'PEP',
#  'RUN',
#  'SEE',
#  'SON',
#  'STX',
#  'SVCO',
#  'SYK',
#  'THRM',
#  'UBER',
#  'VFC',
#  'VFS']