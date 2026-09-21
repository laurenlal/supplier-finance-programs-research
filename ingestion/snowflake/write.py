import os
from snowflake.connector.pandas_tools import write_pandas


def write_df(conn, df, table_name):
    table_name = table_name

    success, nchunks, nrows, output = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name.upper(),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    if not success:
        raise RuntimeError(f"Failed to write dataframe to {table_name}")

    return nrows