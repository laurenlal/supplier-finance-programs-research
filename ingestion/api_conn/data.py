import calcbench as cb
from api_conn.client import initialize_calcbench
from datetime import datetime, timezone
import pandas as pd 
from snowflake.write import write_df
from snowflake.connection import get_snowflake_connection

cb = initialize_calcbench()

def ingestion_staging(df, fiscal_year):
    #reset index
    df = df.reset_index()

    #confirm datatypes for snowflake ingestion
    df["CIK"] = df["CIK"].astype("string").str.zfill(10)
    df["period_start"] = pd.to_datetime(df["period_start"], errors='coerce').dt.date
    df["period_end"] = pd.to_datetime(df["period_end"], errors='coerce').dt.date
    

    #set metadata
    df["ingested_at"] = datetime.now(timezone.utc)
    df["source_system"] = "calcbench"

    df.columns = [col.upper() for col in df.columns]

    return df

def get_financial_data(ticker, fiscal_year):

    metrics = [
    # -------------------------
    # Supplier Finance Program
    # -------------------------
    "SupplierFinanceProgramObligation",
    "SupplierFinanceProgramObligationIncrease",
    "SupplierFinanceProgramObligationSettlement",

    # -------------------------
    # Income Statement
    # -------------------------
    "Revenue",
    "CostOfRevenue",
    "GrossProfit",
    "OperatingIncome",
    "EBIT",
    "EBITDA",
    "NetIncome",
    "InterestExpense",

    # -------------------------
    # Balance Sheet
    # -------------------------
    "Cash",
    "ShortTermInvestments",
    "AccountsReceivable",
    "Inventory",
    "CurrentAssets",
    "Assets",
    "AccountsPayable",
    "CurrentLiabilities",
    "Liabilities",
    "ShortTermDebt",
    "CurrentLongTermDebt",
    "LongTermDebt",
    "TotalDebt",
    "StockholdersEquity",

    # -------------------------
    # Cash Flow
    # -------------------------
    "OperatingCashFlow",
    "CAPEX",
    "CAPEXgross",
    "PaymentsOfDividends",
    "FinancingCashFlow",
    "InvestingCashFlow",

    # -------------------------
    # Working Capital Changes
    # -------------------------
    "PayablesIncreaseDecrease",
    "ReceivablesIncreaseDecrease",
    "InventoryIncreaseDecrease",
    "AccruedLiabilitiesIncreaseDecrease",

    # -------------------------
    # Market / Size
    # -------------------------
    "MarketCapAtEndOfPeriod",
    "EnterpriseValue",
    "SharesOutstandingEndOfPeriod",
    "EndOfPeriodStockPrice",
    "EntityPublicFloat",

    #--------------------------
    # Validation Metrics
    # --------------------------
     "DaysPayablesOut",
        "DaysSalesOut",
        "DaysInventoryHeld",
        "CashToCashCycle",
        "InventoryTurn",
        "PayablesTurn",
        "CurrentRatio",
        "QuickRatio",
        "FreeCashFlow",
        "DebtToEBITDA",
        "GrossProfitMargin",
    ]

    try:
        data = cb.standardized(
            company_identifiers=ticker,
            metrics=metrics,
            fiscal_year=fiscal_year,
            fiscal_period=0
        )
        data = ingestion_staging(data, fiscal_year)
        return data
    
    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        return None


def get_text_data(ticker, fiscal_year):

    metrics = [
    "standard_industrial_classification",
    "filer_category",
    "is_ifrs",
    "sec_html_url",
    "auditor_name"
]

    try:
            data = cb.standardized(
                company_identifiers=ticker,
                metrics=metrics,
                fiscal_year=fiscal_year,
                fiscal_period=0
            )
            data = data.reset_index()
            data["value"] = data["value"].astype("string")
            data.columns = [col.upper() for col in data.columns]



            return data
    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        return None


def get_co_data():
    df = cb.companies()
    df.columns = [col.upper() for col in df.columns]

    conn = get_snowflake_connection()
    write_df(conn=conn, df=df, table_name="COMPANIES")
    print("**** COMPANIES Table Successfully Loaded *******")
    return None