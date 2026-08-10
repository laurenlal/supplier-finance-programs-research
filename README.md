# supplier-finance-programs-research

This repository contains analysis scripts and utilities used to study Supplier Finance Programs (SFP) using Calcbench and internal datasets. The main Python scripts (from the main branch) are documented below with a short description of their purpose, main functions/classes, dependencies, and example usage.

Files
-----

1) cleanse.py

- Purpose: A comprehensive data-cleaning and reporting class for the SFP dataset. The file defines the sfp class which encapsulates dataset loading, filtering, feature engineering, matching procedures, and several report/export utilities (Excel and PDF).

- Key functionality:
  - sfp.build_df(): reads the raw CSV (hard-coded path in the class) and runs the full cleanse and feature pipeline.
  - Filtering utilities: filter_year(), drop_duplicates(), dpo_clean(), clean_dtype(), map_sic(), add_features(), etc.
  - Matching & sampling: match_revenue_distribution(), match_revenue_and_industry_distribution() to create comparison cohorts.
  - Reporting: metric_report_pdf(), compare_summary_pdf(), excel() to export multiple sheets and visualizations.
  - Small helpers: pivotAuditors(), top25_users(), settle_distr(), summary_stats(), and others.

- Dependencies: pandas, numpy, matplotlib, seaborn, pandasql, openpyxl, calcbench, pathlib, re

- Notes and usage:
  - The class references a hard-coded CSV path in build_df(); adjust that path or pass data frames directly when using.
  - Calcbench credentials are read from environment variables in some scripts or set directly in code when used.
  - Typical usage (interactive or script):
      from cleanse import sfp
      sf = sfp()
      df = sf.build_df()          # loads and prepares the dataset
      stats = sf.summary_stats(df)
      sf.excel(df)                # writes output Excel and visualizations

2) disclosure.py

- Purpose: Lightweight text-processing utilities to parse SFP disclosure text and extract structured signals (program category and payment-term buckets).

- Key functions:
  - categorize_program(text): classifies disclosure text into 'Debt', 'Accounts Payable', 'Hybrid / Ambiguous', or 'Unknown' based on keyword heuristics.
  - extract_payment_terms(text): extracts numeric payment-term expressions (e.g., "60 days", "60-90 days") and buckets them ("<45 days", "45–60 days", "60–90 days", etc.).
  - parse_sfp_disclosures(input_file, text_column='Disclosure', output_file='parsed_results.csv'): reads an Excel/CSV file, runs the classifiers, and saves a CSV with two new columns (SFP_Category, Payment_Terms).

- Dependencies: pandas, re, numpy

- Example:
    python disclosure.py
  (or import parse_sfp_disclosures from other scripts to run programmatic parsing.)

3) findold.py

- Purpose: An analysis notebook-style script that compares prior-year (PY) and current-year (CY) SFP user lists. It contains filtering logic, quick summaries, and lists of tickers that differ between datasets.

- Contents & behavior:
  - Loads 'data/py_users.csv' and 'data/original.csv', marks SFP users, applies the same fiscal-year eligibility filters, and computes differences in ticker lists.
  - Intended as an exploratory / one-off script (not a reusable library function).

- Dependencies: pandas, numpy, matplotlib, seaborn, pandasql, openpyxl, calcbench

- Usage:
  - Run from the repo root where the expected 'data/' CSVs exist (e.g., python findold.py) or open it in an interactive environment (Jupyter / VS Code) to step through.

4) get.py

- Purpose: Uses the Calcbench API to search company disclosures for SFP-related terms, collects results, and filters to disclosures that match keyword lists.

- Behavior & key bits:
  - Sets up Calcbench credentials (note: in the version on main branch credentials are set inline — replace with environment-based credentials for safety).
  - Instantiates sfp() from cleanse.py to access its lrg_user dataframe and the tickers to search.
  - Runs cb.disclosure_search for several search terms and accumulates results into a DataFrame, deduplicates, and filters by keywords.

- Dependencies: calcbench, pandas, tqdm, requests, cleanse (local)

- Example usage:
    python get.py
  Pre-requisites:
  - Calcbench credentials must be configured (either by modifying the script or exporting credentials to environment variables if adjusted).
  - The underlying data and/or the cleanse.sfp object must be available (the script expects sf.lrg_user to exist).

5) newdata.py

- Purpose: Example helper script that demonstrates pulling an additional Calcbench metric for a set of tickers and merging that metric into the sfp.lrg_user dataframe, then writing an inventory Excel.

- Behavior:
  - Reads credentials from the environment (CALCBENCH_USER / CALCBENCH_PASS) and sets Calcbench credentials.
  - Uses sfp() from cleanse.py to obtain a base dataframe, queries Calcbench for a chosen metric (e.g., CashToCashCycle), pivots and merges the metric back into the dataframe, applies a ticker whitelist, and writes an inventory Excel file.

- Dependencies: os, calcbench, pandas, tqdm, requests, cleanse (local), openpyxl

- Example usage:
    export CALCBENCH_USER=your_user
    export CALCBENCH_PASS=your_pass
    python newdata.py

Notes, credentials, and safety
------------------------------
- Several scripts set Calcbench credentials directly in the code. For safety, prefer exporting credentials as environment variables and using os.environ (the repository already uses CALCBENCH_USER/CALCBENCH_PASS in some places).
- The code expects certain data files (e.g., data/original.csv, data/py_users.csv) and may include hard-coded paths — verify and update paths to match your environment before running.
- Many scripts are intended for interactive/analytical usage (not hardened CLI tools). Consider refactoring common functionality (data loading, credential handling) into reusable functions if you plan to run these frequently or share with others.

If you'd like, next steps I can take:
- Update the README with usage examples that include environment setup and exact commands to run each script (I can add quick commands for each script).
- Open a PR on main that pulls the Python files into this branch and updates README in-place.
- Create small wrappers (CLI entrypoints) so each script can be executed cleanly with arguments (input paths, output paths, credentials via env).

Which of the next steps would you like? (Choose one)
