import pandas as pd
import calcbench as cb
from api_conn.client import initialize_calcbench
from snowflake.write import write_df
import datetime as dt 


#Grabs all companies in the universe from calcbench api 
def get_companies():
    companies = cb.companies()
    companies = companies[companies["most_recent_fiscal_year"] > 2022]
    tickers = (
        companies["ticker"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )
    return tickers

#batches the companies for api calls when writting to snowflake 
def create_batch(items, batch_size):
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def generate_batch_id():
    """Generate a unique batch identifier for API ingestion batches."""
    return f"batch_{dt.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"



