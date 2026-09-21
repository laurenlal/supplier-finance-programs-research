from api_conn.data import get_financial_data, get_text_data
from api_conn.company import get_companies, create_batch, generate_batch_id

from snowflake.connection import get_snowflake_connection
from snowflake.write import write_df



#(1) Test Snowflake Connection
try: 
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    print("**** Successfully connected to snowflake ****")
except:
    print('ERROR IN SNOWFLAKE CONNECTION')


#(2) Grab data and pull from api

for yr in [2023, 2024, 2025]:
    tickers = get_companies()

    for batch_number, company_batch in enumerate(
        create_batch(tickers, 500),
        start=1
    ):
        print(
            f"Batch {batch_number}: "
            f"{len(company_batch)} companies"
        )

        #Query CB DATA
        #df = get_financial_data(company_batch, fiscal_year=yr)
        df = get_text_data(company_batch, fiscal_year=2023)
        batch_id = generate_batch_id()
        df["BATCH_ID"] = batch_id
        print("** Calcbench data successfully retrieved ***")

        #WRITE TO SNOW
        #write_df(conn, df, "FINANCIALS")
        write_df(conn, df, "METADATA")
        print(f"Batch {batch_number} completed")

conn.close()

#task: run for fy 2023, 2024, 2025
#task: run text_data for fy 2023, 2024, 2025 