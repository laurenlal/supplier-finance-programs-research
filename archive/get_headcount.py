import pandas as pd
import numpy as np
import calcbench as cb

"""
This file is for developing a headcount of all firms in the universe
"""



#---------Connect to Calcbench-----------
try:
    cb.set_credentials("jdmathis@iu.edu", "9Cte&G}n5DTvgn")
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

#< ------------ Get data from csv and prep -------------> 
data = pd.read_csv('data/sfp-test.csv')

tickers = data["ticker"]

ticker_list= tickers.dropna().unique().tolist()



# <------------- define functions --------------->
"""
Filter dataframe (df) for fiscal year with our time parameters (yr)
TO-DO: FIX WITH FILTER FOR FISCAL YEAR
"""
def filter_year(df, yr):
    py = yr - 1 
    ny = yr + 1

   

    df["fiscal_period"] = pd.to_datetime(df["FiscalYearEndDate"], errors="coerce")
    df = df[df["fiscal_year"] == yr]
    cutoff = pd.Timestamp(f"{py}-12-15")
    df["eligible"] = df["fiscal_period"] > cutoff

    #grab data before the 2nd cutoff date 
    cutoff2 = pd.Timestamp(f"{ny}-12-14")
    df["eligible2"] = df["fiscal_period"] > cutoff2

    

    df = df[df["eligible"] == True ]
    df = df[df["eligible2"] == False ]
    return df.drop(columns=["eligible", "eligible2"])

#add columns to df of new metrics
def get_data(df, ticker_list, metrics, year):
    #Connect to CB
    try:
        cb.set_credentials("jdmathis@iu.edu", "9Cte&G}n5DTvgn")
        print(f"Connected to Calcbench")
    except Exception as e:
        print(f"Error setting credentials: {e}")

    
    #grab the data
    raw = cb.standardized(
        company_identifiers=ticker_list,
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
    wide = wide.merge(df, on="ticker", how="left", )
    return wide 


def map_sic(df):
        df['SIC'] = df['SIC'].astype(float)

        conditions = [
            (df['SIC'] <= 1799),       
            (df['SIC'] >= 2000) & (df['SIC'] <= 3999),          
            (df['SIC'] >= 4000) & (df['SIC'] <= 4999),          
            (df['SIC'] >= 5000) & (df['SIC'] <= 5999),          
            (df['SIC'] >= 6000) & (df['SIC'] <= 6799),          
            (df['SIC'] >= 7000) & (df['SIC'] <= 8999),          
            (df['SIC'] >= 9000) & (df['SIC'] <= 9999)           
        ]

        values = [
            "Agriculture, Mining, Construction",
            "Manufacturing",
            "Transportation/Communications/Utilities",
            "Wholesale and Retail Trade",
            "Finance, Insurance, And Real Estate",
            "Services",
            "Public Administration"
        ]

        df['Industry'] = np.select(conditions, values, default="Unknown")
        return df

#prepares dataframe for export 
def prep_data(data, yr):

    df = filter_year(data, yr)

    #add US vs Foreign columns
    df["US_vs_Foreign"] = np.where(
        df["Country"] == "United States",
        "US",
        "Foreign"
    )
    df["Foreign_ifrs"] = np.where(
        (df["is_ifrs"] == True) & (df["US_vs_Foreign"] == "Foreign"),
        1,
        0
    )
    df['user'] = np.where(df["SupplierFinanceProgramObligation"].isna(), 0, 1)

    df = map_sic(df)

    #filter rev > 1 billion
        
    df["Revenue"] = (
    df["Revenue"]
      .astype(str)
      .str.replace(r"[\$,]", "", regex=True)
      .str.replace(r"\((.*)\)", r"-\1", regex=True)
)

    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
    df = df[df["Revenue"] >= 1000000000 ]

    return df

    
def to_excel(df, name, sheet_name):
    with pd.ExcelWriter(f"excels/{name}.xlsx") as writer:
        df.to_excel(writer, sheet_name=f"{sheet_name}", index=False)
# <--------------- run model ------------->



newdf_24 = prep_data(data, 2024)
newdf_23 = prep_data(data, 2023)
newdf_22 = prep_data(data, 2022)

#TO-DO: write above to excel
with pd.ExcelWriter(
    'headcount.xlsx',
    engine='openpyxl'
) as writer:
    newdf_24.to_excel(writer, sheet_name="2024_All_Firms", index=False)
    newdf_23.to_excel(writer, sheet_name="2023_All_Firms", index=False)
    newdf_22.to_excel(writer, sheet_name="2022_All_Firms", index=False)
#TO-DO: put together short summary of total firms, etc. 



