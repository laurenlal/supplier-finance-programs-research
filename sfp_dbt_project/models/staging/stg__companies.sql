with base as (select * 

from {{ source('calcbench', 'COMPANIES') }}
),

clean as (
    select
        trim(TICKER)                                            as ticker,
        trim(ENTITY_NAME)                                       as entity_name,
        entity_id                                               as entity_id,
        entity_code                                             as entity_code,
        try_cast(most_recent_filing as date)                    as most_recent_filing,
        try_cast(most_recent_full_year_end as integer)          as most_recent_full_year_end,
        try_cast(most_recent_complete_calendar_year as integer) as most_recent_complete_calendar_year,
        try_cast(most_recent_complete_fiscal_year as integer)   as most_recent_complete_fiscal_year,
        try_cast(MOST_RECENT_FILING_CALENDAR_PERIOD as integer) as most_recent_filing_calendar_period,
        try_cast(first_filing as date)                          as first_filing,
        naics_code,
        try_cast(sic_code as integer) as sic_code,
        siccategory,
        sicgroupminorgrouptitle,
        trim(CIK_CODE) as cik,
        naics,
        INGESTED_AT,
        SOURCE_SYSTEM

    from base
)

select * from clean