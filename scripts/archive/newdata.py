
import os

import calcbench as cb
import pandas as pd
from tqdm import tqdm
import requests
import os 
from scripts.archive.cleanse import sfp


# credentials used by calcbench
CALCBENCH_USER = os.environ.get('CALCBENCH_USER')
CALCBENCH_PASS = os.environ.get('CALCBENCH_PASS')


cb.set_credentials(CALCBENCH_USER, CALCBENCH_PASS)

f = sfp()

# tickers = f.df.ticker.dropna().unique().tolist()

# df = cb.standardized(
#     company_identifiers=tickers,
#     metrics = ["is_ifrs", "supplierfinanceprogramobligationsettlement"],
#     fiscal_year=2024,
#     fiscal_period=0

# )

# #pivot the tuple 
# df_clean = (
#     df.pivot_table(
#         index="ticker",
#         columns="metric",
#         values="value",
#         aggfunc="first"
#     )
#     .reset_index()
# )

# df_clean.columns.name = None

# #merge to og data set 
# df_merge = f.df.merge(
#     df_clean[["ticker", "is_ifrs"]],
#     on="ticker",
#     how="left"
# )

# #now, df has "is_ifrs" column

data = f.lrg_user #change to whatever df you want to add it to 

tickers = data.ticker.dropna().unique().tolist()

metric = "CashToCashCycle" #change to whatever metric you want to add 

df = cb.standardized(
    company_identifiers=tickers,
    metrics = [metric],
    fiscal_year=2024,
    fiscal_period=0

)

#pivot the tuple 
df_clean = (
    df.pivot_table(
        index="ticker",
        columns="metric",
        values="value",
        aggfunc="first"
    )
    .reset_index()
)

df_clean.columns.name = None

#merge to og data set 
f.lrg_user = f.lrg_user.merge(
    df_clean[["ticker", metric]],
    on="ticker",
    how="left"

)

#Filter out bad tickers (for updated users) 

keep_tickers = [
    "UBER","ASML","ANF","ADM","KR","LYB","MDT","HAL","VZ","EL","MMM","JNJ","BSX","T",
    "RL","PVH","VFC","NEE","TPR","DD","ALV","SEE","CAG","PM","HWM","TGT","CCK","ORLY",
    "CPB","SJM","LECO","TTMI","MDLZ","GPC","HD","WMT","INGM","BA","CI","KVUE","OTIS",
    "GEHC","AGCO","RH","SMG","MAS","WAB","XYL","WCC","ARCO","X","CAT","PEP","KO","PG",
    "CRI","WDC","TAP","HON","BC","MOD","ATR","ZKH","CMI","MELI","TEX","PPC","MSI","KMB",
    "IBM","DOW","PFE","ITT","NWL","CLX","DECK","LOW","ARW","BALY","AAP","ASIX","AQN",
    "AMCR","APOG","ATI","AVY","BALL","BBY","CAL","CHX","CHTR","CMPR","CLF","CNH","COKE",
    "COHR","STZ","CPNG","DAN","DKS","DDS","DLTR","DOV","EMN","ESLT","FDX","FERG","FLEX",
    "FND","FLS","FMC","F","FYBR","FUL","GAP","GTX","GEV","GE","GIS","GM","THRM","GT",
    "GPK","HBI","HAS","HSY","HNI","HUBB","IDXX","IR","INGR","KMT","KDP","KSS","KTB",
    "DNUT","LEG","LKQ","LULU","M","MGA","MAT","NKE","OI","PH","PPG","RRX","REYN","ROST",
    "RPM","STX","SHW","SIG","SLGN","SON","SWK","SCS","RUN","SYY","FTI","TSCO","UA","UPS",
    "VSCO","WBD","WHR","KLG","WKC","YETI","SW","IP","DELL","CPRI","QSR","SPR","DG","TXT",
    "MNRO","ASO","SYK","XRX","AXTA"
]

# standardize tickers (IMPORTANT)
inv_df = f.lrg_user
inv_df["ticker"] = inv_df["ticker"].str.upper()

# filter
inv_df = inv_df[inv_df["ticker"].isin(keep_tickers)]

# sort alphabetically
inv_df = inv_df.sort_values("ticker").reset_index(drop=True)

#(3) WRITE TO EXCEL TO COPY PASTE INTO PALMER FILE
with pd.ExcelWriter("inventory.xlsx", engine="openpyxl") as writer:
                inv_df.to_excel(writer, sheet_name="Inventory", index=False)