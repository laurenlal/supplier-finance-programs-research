**TO-DOs:**

- [ ] ingestion layer: develop script for data refreshes to not overwrite current information and only grab new rows
- [ ] join metadata to financials, and company name to financials 
- [ ] convert dtypes (strings back to dates, etc.)
- [ ] remove nulls, remove duplicates, spot outliers 
- [ ] add metrics (manual DPO calculation)
- [ ] create new views / tables that mimic main data 
- [ ] join palmer's manually scrapped data (put into csv in a seperate folder, join)
- [ ] STRETCH: a way to build a comparitive non-user population...not sure if we can do this in sql >> IDEA: python script outside of pipeline that reads table from snowflake and then manipulates with statistical operations then writes back to snowflake 
- [ ] FINALLY: build out semantic layer for cortex integration. dimensions are the variables, but what would the metrics be

**By Pipeline Stage:**
- Staging:
    - [ ] rename columns
    - [ ] cast datatypes
    - [ ] filter out deleted rows
    - [ ] 1:1 mapping of source tables
    - [ ] standarized foundation (lower everything...?)

    Notes: 
    - Some types of transformations that are sort of acceptable in the context of staging layer include **type casting, column renaming, basic computations** (such as KBs to MBs or GBs), categorisation (e.g. using CASE WHEN statements).
    - materialise as views
    - avoid joins 


- Int / Models:
    - [ ] complex business logic (is_sfp_user?)
    - [ ] complex joins / aggregations
    - [ ] calculations and building blocks
    - [ ] pivoting? 

    Notes:
    - Written in format of CTEs
    - don't materialize as tables, but can for dev
    - goal: bring together models that absorb complexity
    - only reference each model in 1 model

- Marts (dim / fct):
    - [ ] final business-ready tables
    - [ ] excel views for palmer 

    Notes:
    - Materialize as tables



**Example Metrics?**
- [ ] large users vs large non users 
- [ ] manufacturing users (each industry)
- [ ] total users across the years 


Sources: https://towardsdatascience.com/staging-intermediate-mart-models-dbt-2a759ecc1db1/

