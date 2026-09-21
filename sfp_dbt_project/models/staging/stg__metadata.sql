with raw as (select * 

from {{ source('calcbench', 'METADATA') }}),

clean as(
    
    select
        trim(ticker)                                                                        as ticker,
        METRIC                                                                              as metric,
        SUBSTRING(fiscal_period, 1, CHARINDEX('-', fiscal_period) - 1)                      AS fiscal_year,
        SUBSTRING(fiscal_period, CHARINDEX('-', fiscal_period) + 1, LEN(fiscal_period))     AS fiscal_period,    
        VALUE                                                                               as value,
        trim(CIK)                                                                           as cik,
        try_cast(PERIOD_START as date)                                                      as period_start,
        try_cast(PERIOD_END as date)                                                        as period_end,
        try_cast(CALENDAR_YEAR as integer)                                                  as calendar_year,
        try_cast(CALENDAR_PERIOD as integer)                                                as calendar_period,
        INGESTED_AT,
        SOURCE_SYSTEM,
        BATCH_ID

    from raw

)

select * from clean

