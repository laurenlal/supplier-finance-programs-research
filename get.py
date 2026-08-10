
import calcbench as cb
import pandas as pd
from tqdm import tqdm
import requests
from cleanse import sfp



cb.set_credentials("jdmathis@iu.edu", "9Cte&G}n5DTvgn")




search_terms = [
    "supplier finance",
    "standard terms",
    "normal terms",
]

results = []

sf = sfp()

df = sf.lrg_user

tickers = df["ticker"].dropna().unique().tolist()


for term in search_terms:
    with tqdm() as bar:
        disclosures = cb.disclosure_search(
            company_identifiers=tickers,
            full_text_search_term=term,
            year=2024,             # or None for all-history
            period=0,              # 0 = annual (10-K)
            use_fiscal_period=True,
            all_history=False,
            disclosure_names=[],   # required: leave empty when using full-text search
            progress_bar=bar
        )

        for d in disclosures:
            try:
                text = d.get_contents_text()
            except:
                text = None

            results.append({
                "ticker": d.ticker,
                "fiscal_year": d.fiscal_year,
                "period": d.fiscal_period,
                "search_term": term,
                "section_name": d.name,
                "filing_date": d.filing_date,
                "sec_url": d.SEC_URL,
                "text": text
            })

results_df = pd.DataFrame(results)


results_df = results_df.sort_values(["ticker", "fiscal_year", "section_name"])
results_df = results_df.drop_duplicates(subset=["ticker", "fiscal_year", "text"])

keywords = [
    "supplier finance",
    "reverse factoring",
    "supply chain finance",
    "structured payable"
]

mask = results_df["text"].str.contains("|".join(keywords), case=False, na=False)
sfp_disclosures = results_df[mask]

