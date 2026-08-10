import pandas as pd 
import numpy as np
import calcbench as cb
import os

"""
This file is for developing new excel sheets for non-users. 
It pulls previously identified tickers, and uses those to grab more 
data from calcbench, grab PY data, and reformat into new excels
that match our current template. 

"""

CALCBENCH_USER = os.environ.get('CALCBENCH_USER')
CALCBENCH_PASS = os.environ.get('CALCBENCH_PASS')

#---------Connect to Calcbench-----------
try:
    cb.set_credentials(CALCBENCH_USER, CALCBENCH_PASS)
    print(f"Connected to Calcbench")
except Exception as e:
    print(f"Error setting credentials: {e}")

us_states = {
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
    'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
    'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
    'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
    'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY',
    'DC'
}


#---------prep data-------------

#Read data from csv 
nu_df = pd.read_csv('data/maindata_nusr_fixed.csv')
usr_df = pd.read_csv('data/maindata_usr_fixed.csv')

#non_users dfs
nu_manuf_df = nu_df[nu_df["Industry"] == 'Manufacturing']
nu_retail_df = nu_df[nu_df["Industry"] == 'Wholesale and Retail Trade']

#user dfs
usr_manuf_df = usr_df[usr_df["Industry"] == 'Manufacturing']
usr_retail_df = usr_df[usr_df["Industry"] == 'Wholesale and Retail Trade']


#grab tickers to consider 
nu_ticker = nu_df['ticker'].dropna().unique().tolist()
usr_ticker = usr_df['ticker'].dropna().unique().tolist()


#------------functions--------------

#filter time for 2023 (PY)
def filter_year(df, yr):
    py = yr - 1 
    ny = yr + 1
    df["fiscal_period"] = pd.to_datetime(df["FiscalYearEndDate"], errors="coerce")
    cutoff = pd.Timestamp(f"{py}-12-15")
    df["eligible"] = df["fiscal_period"] > cutoff

    #grab data before the 2nd cutoff date 
    cutoff2 = pd.Timestamp(f"{ny}-12-14")
    df["eligible2"] = df["fiscal_period"] > cutoff2

    df = df[df["eligible"] == True ]
    df = df[df["eligible2"] == False ]
    return df.drop(columns=["eligible", "eligible2"])


def get_nu_data(year):

    metrics = columns = [
    
   

   "FiscalYearEndDate",
    "Revenue",
    "CostOfRevenue",
    "SGAExpense",
    "GrossProfit",
    "OperatingIncome",
    "EBIT",
    "EBITDA",
    "NetIncome",
    "AccountsReceivable",
    "Assets",
    "CurrentAssets",
    "AccountsPayable",
    "ShortTermDebt",
    "LongTermDebt",
    "TotalDebt",
    "InterestExpense",
    "OperatingCashFlow",
    "CAPEXgross",
    "CAPEX",
    "SupplierFinanceProgramObligation",
    "SupplierFinanceProgramObligationIncrease",
    "SupplierFinanceProgramObligationSettlement",
    "DaysPayablesOut",
    "DaysSalesOut",
    "CashToCashCycle",
    "InventoryTurn",
    "FreeCashFlow",
    "PaymentsOfDividends",
    "ROA",
    "Inventory",
    "is_ifrs",
    "EntityIncorporationStateCountryCode"
]


    #Connect to CB
    try:
        cb.set_credentials(CALCBENCH_USER, CALCBENCH_PASS)
        print(f"Connected to Calcbench")
    except Exception as e:
        print(f"Error setting credentials: {e}")

    #grab the data 
    raw = cb.standardized(
        company_identifiers=nu_ticker,
        metrics=metrics,
        fiscal_year=year,
        fiscal_period=0
    )

    #pivot for formatting
    wide = (
        raw.pivot_table(
            index="ticker",
            columns="metric",
            values="value",
            aggfunc="first"
        )
        .reset_index()
    )

    wide.columns.name = None

    #Merge company info back (SIC - Merge, company name, etc.)
    wide = wide.merge(nu_df[["ticker", "SIC - MERGE", "Company", "Industry"]], on="ticker", how="left", )
    return wide 

def get_usr_data(year):

    metrics = columns = [
    
   

   "FiscalYearEndDate",
    "Revenue",
    "CostOfRevenue",
    "SGAExpense",
    "GrossProfit",
    "OperatingIncome",
    "EBIT",
    "EBITDA",
    "NetIncome",
    "AccountsReceivable",
    "Assets",
    "CurrentAssets",
    "AccountsPayable",
    "ShortTermDebt",
    "LongTermDebt",
    "TotalDebt",
    "InterestExpense",
    "OperatingCashFlow",
    "CAPEXgross",
    "CAPEX",
    "SupplierFinanceProgramObligation",
    "SupplierFinanceProgramObligationIncrease",
    "SupplierFinanceProgramObligationSettlement",
    "DaysPayablesOut",
    "DaysSalesOut",
    "CashToCashCycle",
    "InventoryTurn",
    "FreeCashFlow",
    "PaymentsOfDividends",
    "ROA",
    "Inventory",
    "is_ifrs",
    "EntityIncorporationStateCountryCode"
    ]

    #grab the data 
    raw = cb.standardized(
        company_identifiers=usr_ticker,
        metrics=metrics,
        fiscal_year=year,
        fiscal_period=0
    )

    #pivot for formatting
    wide = (
        raw.pivot_table(
            index="ticker",
            columns="metric",
            values="value",
            aggfunc="first"
        )
        .reset_index()
    )

    wide.columns.name = None

    #Merge company info back (SIC - Merge, company name, etc.)
    wide = wide.merge(usr_df[["ticker", "SIC - MERGE", "Company", "Industry"]], on="ticker", how="left", )
    return wide 


#reformats to match palmer master data (adds in new columns, etc.)
def usr_reformatting(df, year):
    #new column that is calendar period and is 0 in all (after company)
    df["calendar_period"] = 0
    df["calendar_year"] = year

    #CONVERT DTYPES
    numeric_cols = [
        "Revenue",
        "CostOfRevenue",
        "SGAExpense",
        "GrossProfit",
        "OperatingIncome",
        "EBIT",
        "EBITDA",
        "NetIncome",
        "AccountsReceivable",
        "Assets",
        "CurrentAssets",
        "AccountsPayable",
        "ShortTermDebt",
        "LongTermDebt",
        "TotalDebt",
        "InterestExpense",
        "OperatingCashFlow",
        "CAPEXgross",
        "CAPEX",
        "SupplierFinanceProgramObligation",
        "SupplierFinanceProgramObligationIncrease",
        "SupplierFinanceProgramObligationSettlement",
        "DaysPayablesOut",
        "DaysSalesOut",
        "CashToCashCycle",
        "InventoryTurn",
        "FreeCashFlow",
        "PaymentsOfDividends",
        "ROA",
        "Inventory",
        "InventoryIncreaseDecrease",
        "is_ifrs"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    #ADD NEW COLS


    #make INV_BOY (Inv EOY - INV Change) (after acct receivable)
    df["InventoryBOY"] = df["CostOfRevenue"] - df["InventoryTurn"] * df["CostOfRevenue"]
    #Make Avg_Inventory (Inv EOY + Inv BOY / 2) (after inv_EOY)
    df["Avg_Inventory"] = (df["CostOfRevenue"] + df["InventoryBOY"]) / 2
    #make cost of debt (IE / total_Debt) as num and percent to 2 dec (after interest expense)
    try:
        df["CostOfDebt"] = (df["InterestExpense"] / df["TotalDebt"]).round(4)
    except:
        df["CostOfDebt"] = 0
    #Make leverage (total debt / assets) as num and perc to 2 dec (after cost of debt)
    try:
        df["Leverage"] = (df["TotalDebt"] / df["Assets"]).round(4)
    except:
        df["Leverage"] = 0  
    #trade credit (ap / assets) as num and perc to 2 dec (after leverage)
    try:
        df["TradeCredit"] = (df["AccountsPayable"] / df["Assets"]).round(4)
    except:
        df["TradeCredit"] = 0
    #make free cash flow (op cash flow - capex) (after capex gross)
    df["FreeCashFlow"] = df["OperatingCashFlow"] - df["CAPEX"]
    # make Days Inv. Out (RP Avg Inv / Cogs * 365) avg inventory/cogs * 365
    try:
        df["DaysInvOut"] = (df["Avg_Inventory"] / df["CostOfRevenue"] * 365).round(2)
    except:
        df["DaysInvOut"] = 0
    #make inventory turn (Cogs / avg inventory)
    try:
        df["InventoryTurn"] = df["CostOfRevenue"] / df["Avg_Inventory"].round(2)
    except:
        df["InventoryTurn"] = 0
    #make BOY RF Obligation
    try: 
        df["BOY RF Obligation"] = df["SupplierFinanceProgramObligation"] - df["SupplierFinanceProgramObligationIncrease"] + df["SupplierFinanceProgramObligationSettlement"]
    except:
        df["BOY RF Obligation"] = 0
    #make Growth Rate of Obligation
    try:
        df["Growth Rate of Obligations"] = ((df["SupplierFinanceProgramObligation"] - df["BOY RF Obligation"]) / df["BOY RF Obligation"]).round(4)
    except:
        df["Growth Rate of Obligations"] = 0
    #make RF settle as % of Rev
    try:
        df["RF Settle as % of Rev"] = (df["SupplierFinanceProgramObligationSettlement"] / df["Revenue"]).round(4)
    except:
        df["RF Settle as % of Rev"] = 0
    #EOY RF oblig as % of Debt
    try:
        df["EOY RF Obligations_%_Debt"] = (df["SupplierFinanceProgramObligation"] / df["TotalDebt"]).round(4)
    except:
        df["EOY RF Obligations_%_Debt"] = 0
    #EOY RF oblig as % of EOY AP (blank)
    df["EOY RF Obligations_%_EOY AP"] = ""
    #RF % of COG
    try:
        df["RF_%_COGS"] = (df["SupplierFinanceProgramObligationSettlement"] / df["CostOfRevenue"]).round(4)
    except:
        df["RF_%_COGS"] = 0
    #make ROA (RJP) To USE (NI / assets)
    try:
        df["ROA (RJP) TO USE"] = (df["NetIncome"] / df["Assets"]).round(4)
    except:
        df["ROA (RJP) TO USE"] = 0
    #TIER (EBIT) Ebit / interest expense
    try:
        df["TIER (EBIT)"] = (df["EBIT"] / df["InterestExpense"]).round(2)
    except:
        df["TIER (EBIT)"] = 0
    #TIER (EBITDA) ebitda / interest expense
    try:
        df["TIER (EBITDA)"] = (df["EBITDA"] / df["InterestExpense"]).round(2)
    except:
        df["TIER (EBITDA)"] = 0
    df["US_vs_Foreign"] = np.where(
        df["EntityIncorporationStateCountryCode"].isin(us_states),
            "US",
            "Foreign"
    )
    df["Foreign_ifrs"] = np.where(
        (df["is_ifrs"] == 1) & (df["US_vs_Foreign"] == "Foreign"),
        1,
        0
    )

    #fixing col names and such 
        # Rename columns to final output names
    df = df.rename(columns={
        "calendar_period": "calendar period",
        "Revenue": "REV",
        "CostOfRevenue": "COGS",
        "SGAExpense": "SG_A",
        "OperatingIncome": "Op_Income",
        "AccountsReceivable": "AR",
        "InventoryBOY": "INV_BOY",
        "InventoryIncreaseDecrease": "Inv Change",
        "Inventory": "INV_EOY",
        "CurrentAssets": "Current Assets",
        "AccountsPayable": "AP_EOY",
        "ShortTermDebt": "ST_DEBT",
        "CurrentLiabilities": "Current Liabilities",
        "LongTermDebt": "LT_DEBT",
        "TotalDebt": "TOTAL_DEBT",
        "InterestExpense": "Interest_Exp",
        "CostOfDebt": "Cost of Debt",
        "TradeCredit": "Trade Credit (AP/Assets)",
        "OperatingCashFlow": "Operating Cash Flow",
        "CAPEXgross": "CAPEX (gross)",
        "FreeCashFlow": "Free Cash Flow (Op Cash Flow-CAPEX)",
        "SupplierFinanceProgramObligation": "END: Supplier Finance Program Obligation",
        "SupplierFinanceProgramObligationSettlement": "SupplierFinance Program Obligation Settlement",
        "DaysInvOut": "Days Inv. Out (RP Avg Inv/COGS *365)",
        "DaysSalesOut": "Days Sales Out (calcbench)",
        "InventoryTurn": "Inventory Turn (COGS/Avg Inv)",
        "PaymentsOfDividends": "Payments Of Dividends",
        "SIC - MERGE": "Industry",
        "is_ifrs": "is_ifrs"
    })

    # Desired final order
    final_order = [
        "Company",
        "calendar period",
        "calendar_year",
        "REV",
        "COGS",
        "SG_A",
        "GrossProfit",
        "Op_Income",
        "EBIT",
        "EBITDA",
        "NetIncome",
        "AR",
        "INV_BOY",
        "Inv Change",
        "INV_EOY",
        "Avg_Inventory",
        "Current Assets",
        "Assets",
        "AP_BOY",
        "AP_EOY",
        "ST_DEBT",
        "Current Liabilities",
        "LT_DEBT",
        "TOTAL_DEBT",
        "Interest_Exp",
        "Cost of Debt",
        "Leverage",
        "Trade Credit (AP/Assets)",
        "Operating Cash Flow",
        "CAPEX (gross)",
        "Free Cash Flow (Op Cash Flow-CAPEX)",
        "END: Supplier Finance Program Obligation",
        "SupplierFinanceProgramObligationIncrease",
        "SupplierFinance Program Obligation Settlement",
        "BOY RF Obligation",
        "Growth Rate of Obligations",
        "RF Settle as % of Rev",
        "EOY RF Obligations_%_Debt",
        "EOY RF Obligations_%_EOY AP",
        "RF_%_COGS",
        "DPO_FINAL",
        "Days Inv. Out (RP Avg Inv/COGS *365)",
        "Days Sales Out (calcbench)",
        "CCC",
        "Inventory Turn (COGS/Avg Inv)",
        "ROA (RJP) TO USE",
        "TIER (EBIT)",
        "TIER (EBITDA)",
        "Payments Of Dividends",
        "Industry",
        "is_ifrs",
        "EntityIncorporationStateCountryCode",
        "US_vs_Foreign",
        "Foreign_ifrs"
    ]

    # Add missing columns as blanks
    for col in final_order:
        if col not in df.columns:
            df[col] = ""

    # Reorder exactly
    df = df[final_order]

    return df

#reformats to match palmer master data (adds in new columns, etc.)
def nu_reformatting(df, year):
    #new column that is calendar period and is 0 in all (after company)
    df["calendar_period"] = 0
    df["calendar_year"] = year

    #CONVERT DTYPES

    numeric_cols = [
        "Revenue",
        "CostOfRevenue",
        "SGAExpense",
        "GrossProfit",
        "OperatingIncome",
        "EBIT",
        "EBITDA",
        "NetIncome",
        "AccountsReceivable",
        "Assets",
        "CurrentAssets",
        "AccountsPayable",
        "ShortTermDebt",
        "LongTermDebt",
        "TotalDebt",
        "InterestExpense",
        "OperatingCashFlow",
        "CAPEXgross",
        "CAPEX",
        "SupplierFinanceProgramObligation",
        "SupplierFinanceProgramObligationIncrease",
        "SupplierFinanceProgramObligationSettlement",
        "DaysPayablesOut",
        "DaysSalesOut",
        "CashToCashCycle",
        "InventoryTurn",
        "FreeCashFlow",
        "PaymentsOfDividends",
        "ROA",
        "Inventory",
        "InventoryIncreaseDecrease",
        "is_ifrs"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    #ADD NEW COLS


    #make INV_BOY (Inv EOY - INV Change) (after acct receivable)
    df["InventoryBOY"] = df["CostOfRevenue"] - df["InventoryTurn"] * df["CostOfRevenue"]
    #Make Avg_Inventory (Inv EOY + Inv BOY / 2) (after inv_EOY)
    df["Avg_Inventory"] = (df["CostOfRevenue"] + df["InventoryBOY"]) / 2
    #make cost of debt (IE / total_Debt) as num and percent to 2 dec (after interest expense)
    try:
        df["CostOfDebt"] = (df["InterestExpense"] / df["TotalDebt"]).round(4)
    except:
        df["CostOfDebt"] = 0
    #Make leverage (total debt / assets) as num and perc to 2 dec (after cost of debt)
    try:
        df["Leverage"] = (df["TotalDebt"] / df["Assets"]).round(4)
    except:
        df["Leverage"] = 0  
    #trade credit (ap / assets) as num and perc to 2 dec (after leverage)
    try:
        df["TradeCredit"] = (df["AccountsPayable"] / df["Assets"]).round(4)
    except:
        df["TradeCredit"] = 0
    #make free cash flow (op cash flow - capex) (after capex gross)
    df["FreeCashFlow"] = df["OperatingCashFlow"] - df["CAPEX"]
    # make Days Inv. Out (RP Avg Inv / Cogs * 365) avg inventory/cogs * 365
    try:
        df["DaysInvOut"] = (df["Avg_Inventory"] / df["CostOfRevenue"] * 365).round(2)
    except:
        df["DaysInvOut"] = 0
    #make inventory turn (Cogs / avg inventory)
    try:
        df["InventoryTurn"] = df["CostOfRevenue"] / df["Avg_Inventory"].round(2)
    except:
        df["InventoryTurn"] = 0
    #make ROA (RJP) To USE (NI / assets)
    try:
        df["ROA (RJP) TO USE"] = (df["NetIncome"] / df["Assets"]).round(4)
    except:
        df["ROA (RJP) TO USE"] = 0
    #TIER (EBIT) Ebit / interest expense
    try:
        df["TIER (EBIT)"] = (df["EBIT"] / df["InterestExpense"]).round(2)
    except:
        df["TIER (EBIT)"] = 0
    #TIER (EBITDA) ebitda / interest expense
    try:
        df["TIER (EBITDA)"] = (df["EBITDA"] / df["InterestExpense"]).round(2)
    except:
        df["TIER (EBITDA)"] = 0
    df["US_vs_Foreign"] = np.where(
        df["EntityIncorporationStateCountryCode"].isin(us_states),
            "US",
            "Foreign"
    )
    df["Foreign_ifrs"] = np.where(
        (df["is_ifrs"] == 1) & (df["US_vs_Foreign"] == "Foreign"),
        1,
        0
    )

    #fixing col names and such 
        # Rename columns to final output names
    df = df.rename(columns={
        "calendar_period": "calendar period",
        "Revenue": "REV",
        "CostOfRevenue": "COGS",
        "SGAExpense": "SG_A",
        "OperatingIncome": "Op_Income",
        "AccountsReceivable": "AR",
        "InventoryBOY": "INV_BOY",
        "InventoryIncreaseDecrease": "Inv Change",
        "Inventory": "INV_EOY",
        "CurrentAssets": "Current Assets",
        "AccountsPayable": "AP_EOY",
        "ShortTermDebt": "ST_DEBT",
        "CurrentLiabilities": "Current Liabilities",
        "LongTermDebt": "LT_DEBT",
        "TotalDebt": "TOTAL_DEBT",
        "InterestExpense": "Interest_Exp",
        "CostOfDebt": "Cost of Debt",
        "TradeCredit": "Trade Credit (AP/Assets)",
        "OperatingCashFlow": "Operating Cash Flow",
        "CAPEXgross": "CAPEX (gross)",
        "FreeCashFlow": "Free Cash Flow (Op Cash Flow-CAPEX)",
        "SupplierFinanceProgramObligation": "END: Supplier Finance Program Obligation",
        "SupplierFinanceProgramObligationSettlement": "SupplierFinance Program Obligation Settlement",
        "DaysInvOut": "Days Inv. Out (RP Avg Inv/COGS *365)",
        "DaysSalesOut": "Days Sales Out (calcbench)",
        "InventoryTurn": "Inventory Turn (COGS/Avg Inv)",
        "PaymentsOfDividends": "Payments Of Dividends",
        "Industry": "Industry",
        "is_ifrs": "is_ifrs",
        "EntityIncorporationStateCountryCode": "EntityIncorporationStateCountryCode"
    })

    # Desired final order
    final_order = [
        "Company",
        "calendar period",
        "calendar_year",
        "REV",
        "COGS",
        "SG_A",
        "GrossProfit",
        "Op_Income",
        "EBIT",
        "EBITDA",
        "NetIncome",
        "AR",
        "INV_BOY",
        "Inv Change",
        "INV_EOY",
        "Avg_Inventory",
        "Current Assets",
        "Assets",
        "AP_BOY",
        "AP_EOY",
        "ST_DEBT",
        "Current Liabilities",
        "LT_DEBT",
        "TOTAL_DEBT",
        "Interest_Exp",
        "Cost of Debt",
        "Leverage",
        "Trade Credit (AP/Assets)",
        "Operating Cash Flow",
        "CAPEX (gross)",
        "Free Cash Flow (Op Cash Flow-CAPEX)",
        "DPO_FINAL",
        "Days Inv. Out (RP Avg Inv/COGS *365)",
        "Days Sales Out (calcbench)",
        "CCC",
        "Inventory Turn (COGS/Avg Inv)",
        "ROA (RJP) TO USE",
        "TIER (EBIT)",
        "TIER (EBITDA)",
        "Payments Of Dividends",
        "Industry",
        "is_ifrs",
        "EntityIncorporationStateCountryCode",
        "US_vs_Foreign",
        "Foreign_ifrs"
    ]

    # Add missing columns as blanks
    for col in final_order:
        if col not in df.columns:
            df[col] = ""

    # Reorder exactly
    df = df[final_order]

    return df



#--------------------------------------------Execute Process -------------------------------

#--------------2023
py_nu_data = get_nu_data(2023)
py_usr_data = get_usr_data(2023)

py_all_nu = nu_reformatting(py_nu_data, 2023)
py_all_u = usr_reformatting(py_usr_data, 2023)


#------manufacturing dfs 
py_nu_manfu_df = filter_year(py_nu_data[py_nu_data["SIC - MERGE"] == 'Manufacturing'], 2023)
py_nu_manfu_df = nu_reformatting(py_nu_manfu_df, 2023)

py_usr_manfu_df = filter_year(py_usr_data[py_usr_data["SIC - MERGE"] == 'Manufacturing'], 2023)
py_usr_manfu_df = usr_reformatting(py_usr_manfu_df, 2023)


#------retail dfs 
py_nu_retail_df = filter_year(py_nu_data[py_nu_data["SIC - MERGE"] == 'Wholesale and Retail Trade'], 2023)
py_nu_retail_df = nu_reformatting(py_nu_retail_df, 2023)

py_usr_retail_df = filter_year(py_usr_data[py_usr_data["SIC - MERGE"] == 'Wholesale and Retail Trade'], 2023)
py_usr_retail_df = usr_reformatting(py_usr_retail_df, 2023)



def clean_ticker(series):
    return (
        series.astype("string")
        .str.strip()
        .str.upper()
    )

nu_df["ticker"] = clean_ticker(nu_df["ticker"])
usr_df["ticker"] = clean_ticker(usr_df["ticker"])

#------------------2024
cy_nu_data = get_nu_data(2024)
cy_usr_data = get_usr_data(2024)

cy_all_nu = nu_reformatting(cy_nu_data, 2024)
cy_all_u = usr_reformatting(cy_usr_data, 2024)


#------manufacturing dfs
cy_nu_manfu_df = filter_year(cy_nu_data[cy_nu_data["Industry"] == 'Manufacturing'], 2024)
cy_nu_manfu_df = nu_reformatting(cy_nu_manfu_df, 2024)

cy_usr_manfu_df = filter_year(cy_usr_data[cy_usr_data["Industry"] == 'Manufacturing'], 2024)
cy_usr_manfu_df = usr_reformatting(cy_usr_manfu_df, 2024)


#------retail dfs
cy_nu_retail_df = filter_year(cy_nu_data[cy_nu_data["Industry"] == 'Wholesale and Retail Trade'], 2024)
cy_nu_retail_df = nu_reformatting(cy_nu_retail_df, 2024)

cy_usr_retail_df = filter_year(cy_usr_data[cy_usr_data["Industry"] == 'Wholesale and Retail Trade'], 2024 )
cy_usr_retail_df = usr_reformatting(cy_usr_retail_df, 2024)


#------------------2022
ppy_nu_data = get_nu_data(2022)
ppy_usr_data = get_usr_data(2022)

ppy_all_nu = nu_reformatting(ppy_nu_data, 2022)
ppy_all_u = usr_reformatting(ppy_usr_data, 2022)


#------manufacturing dfs
ppy_nu_manfu_df = filter_year(ppy_nu_data[ppy_nu_data["Industry"] == 'Manufacturing'], 2022)
ppy_nu_manfu_df = nu_reformatting(ppy_nu_manfu_df, 2022)

ppy_usr_manfu_df = filter_year(ppy_usr_data[ppy_usr_data["Industry"] == 'Manufacturing'], 2022)
ppy_usr_manfu_df = usr_reformatting(ppy_usr_manfu_df, 2022)


#------retail dfs
ppy_nu_retail_df = filter_year(ppy_nu_data[cy_nu_data["Industry"] == 'Wholesale and Retail Trade'], 2022)
ppy_nu_retail_df = nu_reformatting(ppy_nu_retail_df, 2022)

ppy_usr_retail_df = filter_year(ppy_usr_data[ppy_usr_data["Industry"] == 'Wholesale and Retail Trade'], 2022)
ppy_usr_retail_df = usr_reformatting(ppy_usr_retail_df, 2022)


# to_excel()
def to_excel():

    #all firm sheet 2022
    with pd.ExcelWriter('excels/all_firms_2022.xlsx') as writer:
        ppy_all_nu.to_excel(writer, sheet_name='Non-Users 2022', index=False)
        ppy_all_u.to_excel(writer, sheet_name='Users 2022', index=False)

    #all firm sheet 2023
    with pd.ExcelWriter('excels/all_firms_2023.xlsx') as writer:
        py_all_nu.to_excel(writer, sheet_name='Non-Users 2023', index=False)
        py_all_u.to_excel(writer, sheet_name='Users 2023', index=False)

    #historical sheet 
    with pd.ExcelWriter('excels/historical_users.xlsx') as writer:
        ppy_all_u.to_excel(writer, sheet_name='Users 2022', index=False)
        py_all_u.to_excel(writer, sheet_name='Users 2023', index=False)
        cy_all_u.to_excel(writer, sheet_name='Users 2024', index=False)
    
    #all firm sheet 2024
    with pd.ExcelWriter('excels/all_firms_2024.xlsx') as writer:
        cy_all_nu.to_excel(writer, sheet_name='Non-Users 2024', index=False)
        cy_all_u.to_excel(writer, sheet_name='Users 2024', index=False)

    #manufacturing sheet
    with pd.ExcelWriter('excels/manufacturing_firms.xlsx') as writer:
        ppy_nu_manfu_df.to_excel(writer, sheet_name='Non-Users 2022', index=False)
        py_nu_manfu_df.to_excel(writer, sheet_name='Non-Users 2023 ', index=False)
        cy_nu_manfu_df.to_excel(writer, sheet_name='Non-Users 2024', index=False)
        ppy_usr_manfu_df.to_excel(writer, sheet_name='Users 2022', index=False)
        py_usr_manfu_df.to_excel(writer, sheet_name='Users 2023', index=False)
        cy_usr_manfu_df.to_excel(writer, sheet_name='Users 2024', index=False)


    #retail sheet 
    with pd.ExcelWriter('excels/retail_firms.xlsx') as writer:
        ppy_nu_retail_df.to_excel(writer, sheet_name='Non-Users 2022', index=False)
        py_nu_retail_df.to_excel(writer, sheet_name='Non-Users 2023', index=False)
        cy_nu_retail_df.to_excel(writer, sheet_name='Non-Users 2024', index=False)
        ppy_usr_retail_df.to_excel(writer, sheet_name='Users 2022', index = False)
        py_usr_retail_df.to_excel(writer, sheet_name='Users 2023', index=False)
        cy_usr_retail_df.to_excel(writer, sheet_name='Users 2024', index=False)

to_excel()

