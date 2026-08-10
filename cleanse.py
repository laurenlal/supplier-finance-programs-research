import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from pandasql import sqldf
from openpyxl import load_workbook
from openpyxl.styles import numbers
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import calcbench as cb
import re
from pathlib import Path

# credentials used by calcbench
CALCBENCH_USER = os.environ.get('CALCBENCH_USER')
CALCBENCH_PASS = os.environ.get('CALCBENCH_PASS')




class sfp:

    #filter based on annual data and only 2024 

    
    def __init__(self):
        #uniform color pallette 
        self.CUSTOM_BLUE_PALETTE = [
    "#1f3f77",  
    "#a9c9ff", 
    "#4a66a6",  
    "#6f95d1",  
    "#5aa9e6",  
    "#6c6ebf",  
    "#4f3f99",  
    "#5a6f8f",  
    "#2f647f",  
]
        # self.df = self.build_df()
        # self.lrg_user = self.get_user(self.get_lrg_mkt(self.df))
        # self.lrg_nuser = self.get_non_user(self.get_lrg_mkt(self.df))
        # self.mid_user = self.get_user(self.get_mid_mkt(self.df))
        # self.mid_nuser = self.get_non_user(self.get_mid_mkt(self.df))
       # self.excel(self.df)
       # self.run_report()

    #reads and wrangles data 
    def build_df(self):
        df = pd.read_csv('/Users/laurenlal/ACCT2610TA/calcbench/data/original.csv')
        df = self.filter_year(df)
        df = self.map_sic(df)
        df = self.clean_dtype(df)
        df = self.add_features(df)
        df = self.drop_duplicates(df)
        df = self.dpo_clean(df)
        df = self.addData(df, "auditor_name") #add auditor name to df

        return df
    

    #adds IFRS column to the dataset
    def add_data(self, df, metric):
        cb.set_credentials(CALCBENCH_USER, CALCBENCH_PASS)

        tickers = df.ticker.dropna().unique().tolist()

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
        df_merge = df.merge(
            df_clean[["ticker", metric]],
            on="ticker",
            how="left"
        )

        #now, df has "metric" column
        return df_merge

    #compairson function for arbitrarily built non-user sample population that mimics users 
    #develops new sample, then runs a comparison report, then calculates updated DPOS
    def run_comparison(self):
        updated_nuser, diagnostic = self.match_revenue_and_industry_distribution(self.lrg_user, self.lrg_nuser)
        self.compare_summary_pdf(self.lrg_user, updated_nuser, name1="Large SFP Users", name2="Matched Large Non-SFP Users")
        print(diagnostic)


    #DESCRIPTION: filters any data set to be in specific year that we need
    def filter_year(self, df):
        #convert fiscal year end to datetime
        df["fiscal_period"] = pd.to_datetime(df["FiscalYearEndDate"], errors="coerce")

        #grab data after the cutoff date 
        cutoff = pd.Timestamp("2023-12-15")
        df["eligible"] = df["fiscal_period"] > cutoff

        #grab data before the 2nd cutoff date 
        cutoff2 = pd.Timestamp("2025-12-14")
        df["eligible2"] = df["fiscal_period"] > cutoff2

        df = df[df["eligible"] == True ]
        df = df[df["eligible2"] == False ]
        df = df[df["calendar_period"] == 0]
        df = df.drop(columns=["eligible", "eligible2"])
        return df

    #Identifies companies with duplicate entries 
    def find_duplicates(self, df):
        duplicates = df[df.duplicated(subset="Company")]
        dups = duplicates["Company"].tolist()
        print(dups)
        return dups

    # All of these values are in the middle market and are non-users
    #drops duplicates by keeping the most recent fiscal year entry 
    def drop_duplicates(self, df):
        self.find_duplicates(df)
        df = df.sort_values("fiscal_period", ascending=False)
        df = df.drop_duplicates(subset="Company", keep="first")
        return df
 
    #re-map the SIC codes 
    def map_sic(self, df):
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

    def clean_dtype(self, df):
        print(df)
        for col in df.columns:
            try:
                df[col] = (df[col].replace(r'[\$,]', '', regex=True)     
                                .replace('Missing value', np.nan)      
                                .astype(float)                          
                                .astype("Int64"))
            except:
                pass 

        #convert dtypes 
        df["Revenue"] = (pd.to_numeric(df["Revenue"].replace('[\$,]', '', regex=True), errors="coerce").astype("Int64"))
        df["AccountsPayable"] = (pd.to_numeric(df["AccountsPayable"].replace('[\$,]', '', regex=True), errors="coerce").astype("Int64"))
        df["CostOfRevenue"] = (pd.to_numeric(df["CostOfRevenue"].replace('[\$,]', '', regex=True), errors="coerce").astype("Int64"))
        df["SupplierFinanceProgramObligationSettlement"] = (pd.to_numeric(df["SupplierFinanceProgramObligationSettlement"].replace('[\$,]', '', regex=True), errors="coerce").astype("Int64"))
        df["NetIncome"] = (pd.to_numeric(df["NetIncome"].replace('[\$,]', '', regex=True), errors="coerce").astype("Int64"))
        df["Assets"] = (pd.to_numeric(df["Assets"].replace('[\$,]', '', regex=True), errors="coerce").astype("Int64"))
        df["CCC"] = (pd.to_numeric(df["CCC"].replace('[\$,]', '', regex=True), errors="coerce").astype("double"))
        df["TotalDebt"] = (pd.to_numeric(df["TotalDebt"].replace('[\$,]', '', regex=True), errors="coerce").astype("double"))
        df["CAPEX"] = (pd.to_numeric(df["CAPEX"].replace('[\$,]', '', regex=True), errors="coerce").astype("double"))
        df["OperatingCashFlow"] = (pd.to_numeric(df["OperatingCashFlow"].replace('[\$,]', '', regex=True), errors="coerce").astype("double"))

        return df

    #Adding featuers (can add more)
    def add_features(self, df):
        #manual DPO
        df["DPO - Manual"] = (df["AccountsPayable"] / df["CostOfRevenue"]) * 365

        #ROA
        df["ROA"] = (df["NetIncome"] / df["Assets"])
        df["ROA"] = df["ROA"].replace([np.inf, -np.inf], np.nan) 

        #Leverage 
        df["Leverage"] = df["TotalDebt"] / df["Assets"]

        #Financial Commitement 
        df["FinancialCommit"] = df["CAPEX"] - df["OperatingCashFlow"]

        #Credit Risk
        df["Trade Credit"] = df["AccountsPayable"] / df["Assets"]
        
        #sfp % of rev
        df["sfp_perc_rev"] = df["SupplierFinanceProgramObligationSettlement"] / df["Revenue"]
    
        df["adjusted_DPO"] = df["DPO - Manual"] - (df["SupplierFinanceProgramObligationSettlement"] / df["CostOfRevenue"]) * 365    

        return df
    #---------------GETTERS--------------------
    # df has 5,803 entries
    def get_lrg_mkt(self, df):
        lrg_mkt = df[df["Market"] == "Large"] #1752
        return lrg_mkt

    def get_mid_mkt(self, df):
        mid_mkt = df[df["Market"] == "Middle"] #4051
        return mid_mkt
    
    def get_user(self, df):
        user_df = df[df["User [ 1 - yes, 0 -no]"] == 1] 
        return user_df

    def get_non_user(self, df):
        nuser_df = df[df["User [ 1 - yes, 0 -no]"] == 0] 
        return nuser_df


    def excel(self, df):
            output_path = "sfp_final_db.xlsx"

            mode = "w" if not os.path.exists(output_path) else "a"
            #grab dfs to write to excel

            #(1) ALL SFP Users (Large Companies)
            sfp_user = self.get_user(self.get_lrg_mkt(df))
            
            #(1a) Top 25 Large Users 
            top25_large_users = self.top25_users(sfp_user)
            
            #(3) ALL NON-SFP Users (Large Companies)
            non_sfp_user = self.get_non_user(self.get_lrg_mkt(df))

            #(4) Size/Industry Adjusted Non-User Group
            adjusted_non_user, diagnostic = self.match_revenue_and_industry_distribution(sfp_user, non_sfp_user)

            #(5) Large SFP Outliers

            #(6) Large Non-SFP Outliers 

            #(7) ALL Middle Market SFP Users
            mid_sfp_user = self.get_user(self.get_mid_mkt(df)) 

            #(8) All Middle Market NON-SFP Users
            mid_non_sfp_user = self.get_non_user(self.get_mid_mkt(df))

            #(9) Visualizations Data 
            #industry_db = self.ind_pie_data_perc()
            img = Image(self.settle_distr())
            img.width = 900
            img.height = 450 

            auditors = self.pivotAuditors(sfp_user)



            with pd.ExcelWriter(output_path, engine="openpyxl", mode=mode, if_sheet_exists="overlay") as writer:
                sfp_user.to_excel(writer, sheet_name="SFP User - Large", index=False)
                top25_large_users.to_excel(writer, sheet_name="Top 25 Large Users", index=False)
                non_sfp_user.to_excel(writer, sheet_name="Non SFP User - Large", index=False)
                adjusted_non_user.to_excel(writer, sheet_name="NEW Non SFP User - Large", index=False)
                mid_sfp_user.to_excel(writer, sheet_name="SFP User - Middle", index=False)
                mid_non_sfp_user.to_excel(writer, sheet_name="Non SFP User - Middle", index=False)
                #industry_db.to_excel(writer, sheet_name="Visualizations", index=False)
            
            wb = load_workbook(output_path)
            sheet_name = "Visualizations"
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
            else:
                ws = wb.create_sheet(sheet_name)
            
            ws._images = []  
            ws.add_image(img, "A1")
            
            # #insert auditor pivot below image
            # start_row = 26
            # start_col = 1  

            # for r_idx, row in enumerate(
            #     dataframe_to_rows(auditors, index=False, header=True),
            #     start=start_row
            # ):
            #     for c_idx, value in enumerate(row, start=start_col):
            #         ws.cell(row=r_idx, column=c_idx, value=value)

            wb.save(output_path)

            print(f"Saved to: {output_path}")

    def run_report(self):
        self.metric_report_pdf(self.lrg_user, title="Large Market SFP Users")
        self.metric_report_pdf(self.lrg_nuser, title="Large Market Non-SFP Users")
        self.metric_report_pdf(self.mid_user, title="Middle Market SFP Users")
        self.metric_report_pdf(self.mid_nuser, title="Middle Market Non-SFP Users")
        print("Reports Generated.")
    

    def summary_stats(self, df):
        #get summary stats
        describe = df.describe(include='all')
        revenue = describe["Revenue"]

        #print
        return describe

    #outputs a pdf report for Revenue given any df (Use for easy comparison between dfs)
    def metric_report_pdf(self, df, title, 
        metric: str = "Revenue",
        bins: int = 50,
        drop_zeros: bool = False,
        add_log_view: bool = True,
    ):
        #error handling
        if metric not in df.columns:
            raise ValueError(f"'{metric}' not found in df columns")

        s = pd.to_numeric(df[metric], errors="coerce").dropna()
        if drop_zeros:
            s = s[s != 0]

        if s.empty:
            raise ValueError(f"No valid numeric values found for '{metric}' after cleaning.")

        # Summary stats (you can add more if you want)
        stats = pd.Series({
            "count": int(s.count()),
            "missing": int(df[metric].isna().sum()),
            "mean": float(s.mean()),
            "std": float(s.std(ddof=1)),
            "min": float(s.min()),
            "Q1": float(s.quantile(0.25)),
            "median": float(s.median()),
            "Q3": float(s.quantile(0.75)),
            "p90": float(s.quantile(0.90)),
            "p95": float(s.quantile(0.95)),
            "max": float(s.max()),
            "skew": float(s.skew()),
            "kurtosis": float(s.kurtosis()),
        })

        report_title = f"{title} Distribution Report"
        pdf_path = f"reports/{title.replace(' ', '_').lower()}_report.pdf"

        with PdfPages(pdf_path) as pdf:
            # Page 1: summary table + histogram
            fig = plt.figure(figsize=(11, 8.5))  # landscape letter-ish
            fig.suptitle(report_title, fontsize=16, y=0.98)

            # Summary table
            ax_table = fig.add_axes([0.05, 0.55, 0.40, 0.38])
            ax_table.axis("off")
            table_data = [[k, f"{v:,.4f}" if isinstance(v, float) else str(v)] for k, v in stats.items()]
            tbl = ax_table.table(cellText=table_data, colLabels=["Statistic", "Value"], loc="center")
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(9)
            tbl.scale(1, 1.2)

            # Histogram
            ax_hist = fig.add_axes([0.52, 0.55, 0.43, 0.38])
            ax_hist.hist(s.values, bins=bins)
            ax_hist.set_title(f"{metric} Histogram")
            ax_hist.set_xlabel(metric)
            ax_hist.set_ylabel("Count")
            ax_hist.grid(True, alpha=0.25)

            # Boxplot (bottom full width)
            ax_box = fig.add_axes([0.05, 0.10, 0.90, 0.32])
            ax_box.boxplot(s.values, vert=False, showfliers=True)
            ax_box.set_title(f"{metric} Boxplot")
            ax_box.set_xlabel(metric)
            ax_box.grid(True, alpha=0.25)

            pdf.savefig(fig)
            plt.close(fig)

            # Optional Page 2: log histogram (great for revenue)
            if add_log_view:
                s_pos = s[s > 0]
                if not s_pos.empty:
                    log_s = np.log10(s_pos)

                    fig2 = plt.figure(figsize=(11, 8.5))
                    fig2.suptitle(f"{report_title} (Log View)", fontsize=16, y=0.98)

                    ax1 = fig2.add_axes([0.08, 0.55, 0.84, 0.33])
                    ax1.hist(log_s.values, bins=bins)
                    ax1.set_title(f"log10({metric}) Histogram (positive values only)")
                    ax1.set_xlabel(f"log10({metric})")
                    ax1.set_ylabel("Count")
                    ax1.grid(True, alpha=0.25)

                    ax2 = fig2.add_axes([0.08, 0.12, 0.84, 0.33])
                    ax2.boxplot(log_s.values, vert=False, showfliers=True)
                    ax2.set_title(f"log10({metric}) Boxplot")
                    ax2.set_xlabel(f"log10({metric})")
                    ax2.grid(True, alpha=0.25)

                    pdf.savefig(fig2)
                    plt.close(fig2)

        return stats

    #comparison report 
    #sf.compare_summary_pdf(sf.lrg_user, sf.lrg_nuser)
    def compare_summary_pdf(self, 
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        metric: str = "Revenue",
        name1: str = "Users",
        name2: str = "NonUsers",
        out_path: str = "reports/compare_summary.pdf",
    ):
        # --- clean series ---
        s1 = pd.to_numeric(df1[metric], errors="coerce").dropna()
        s2 = pd.to_numeric(df2[metric], errors="coerce").dropna()

        if s1.empty or s2.empty:
            raise ValueError(f"'{metric}' has no numeric values in one of the dfs after cleaning.")

        # --- summary stats (keep it basic) ---
        stats1 = {
            "count": int(s1.count()),
            "missing": int(s1.isna().sum()),
            "mean": float(s1.mean()),
            "std": float(s1.std(ddof=1)),
            "min": float(s1.min()),
            "Q1": float(s1.quantile(0.25)),
            "median": float(s1.median()),
            "Q3": float(s1.quantile(0.75)),
            "p90": float(s1.quantile(0.90)),
            "p95": float(s1.quantile(0.95)),
            "max": float(s1.max()),
            "skew": float(s1.skew()),
            "kurtosis": float(s1.kurtosis()),
        }
        stats2 = {
            "count": int(s2.count()),
            "missing": int(s2.isna().sum()),
            "mean": float(s2.mean()),
            "std": float(s2.std(ddof=1)),
            "min": float(s2.min()),
            "Q1": float(s2.quantile(0.25)),
            "median": float(s2.median()),
            "Q3": float(s2.quantile(0.75)),
            "p90": float(s2.quantile(0.90)),
            "p95": float(s2.quantile(0.95)),
            "max": float(s2.max()),
            "skew": float(s2.skew()),
            "kurtosis": float(s2.kurtosis()),
        }

        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

        with PdfPages(out_path) as pdf:
            fig = plt.figure(figsize=(11, 8.5))
            fig.suptitle(f"{metric} Summary Comparison", fontsize=16, y=0.97)

            # left table
            ax1 = fig.add_axes([0.06, 0.12, 0.42, 0.78])
            ax1.axis("off")
            t1 = [[k, f"{v:,.4f}" if isinstance(v, float) else str(v)] for k, v in stats1.items()]
            tbl1 = ax1.table(cellText=t1, colLabels=[name1, ""], loc="center")
            tbl1.auto_set_font_size(False)
            tbl1.set_fontsize(10)
            tbl1.scale(1, 1.4)

            # right table
            ax2 = fig.add_axes([0.52, 0.12, 0.42, 0.78])
            ax2.axis("off")
            t2 = [[k, f"{v:,.4f}" if isinstance(v, float) else str(v)] for k, v in stats2.items()]
            tbl2 = ax2.table(cellText=t2, colLabels=[name2, ""], loc="center")
            tbl2.auto_set_font_size(False)
            tbl2.set_fontsize(10)
            tbl2.scale(1, 1.4)

            pdf.savefig(fig)
            plt.close(fig)

        print(f"Saved: {out_path}")
        return stats1, stats2

    #<---------------- NON USER CONSTRUCTION ------------>
    def construction(self):
        nuser = self.lrg_nuser
        nuser = nuser.sort_values(by="Revenue", ascending=True)

        #Purge 1: Fix Min to Q1 distribution of Users
        user_q1 = self.lrg_user["Revenue"].quantile(0.25)
        purge1 = nuser[nuser["Revenue"] < user_q1]

        

        self.compare_summary_pdf(self.lrg_user, nuser)

    #make a new nonuser df that matches lrg user distribution
    def match_revenue_distribution(
    self,
    good_df: pd.DataFrame,          # reference (e.g., large users)
    bad_df: pd.DataFrame,           # to be matched (e.g., large non-users)
    metric: str = "Revenue",
    quantiles=(0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0),  # good for right-skew
    random_state: int = 42,
    ):
    
    # --- clean series (reference bins come from good_df) ---
        good_s = pd.to_numeric(good_df[metric], errors="coerce")
        bad_s  = pd.to_numeric(bad_df[metric], errors="coerce")

        good_clean = good_df.copy()
        bad_clean  = bad_df.copy()
        good_clean[metric] = good_s
        bad_clean[metric]  = bad_s

        good_clean = good_clean.dropna(subset=[metric])
        bad_clean  = bad_clean.dropna(subset=[metric])

        if good_clean.empty or bad_clean.empty:
            raise ValueError(f"After cleaning, one df has no valid '{metric}' values.")

        # --- compute bin edges from good_df quantiles ---
        edges = good_clean[metric].quantile(list(quantiles)).to_numpy()

        # handle duplicates (can happen if many same revenues)
        edges = np.unique(edges)
        if len(edges) < 3:
            raise ValueError(
                f"Not enough distinct quantile cutpoints for '{metric}'. "
                f"Try fewer quantiles or a different metric."
            )

        # ensure last edge is strictly greater than previous (pd.cut can be picky)
        if edges[-1] == edges[-2]:
            edges[-1] = edges[-1] + 1

        # --- assign bins using GOOD edges ---
        good_bins = pd.cut(good_clean[metric], bins=edges, include_lowest=True)
        bad_bins  = pd.cut(bad_clean[metric],  bins=edges, include_lowest=True)

        good_clean = good_clean.assign(_rev_bin=good_bins)
        bad_clean  = bad_clean.assign(_rev_bin=bad_bins)

        # drop bad rows that fall outside good's range (NaN bin)
        bad_clean_in_range = bad_clean.dropna(subset=["_rev_bin"])

        # --- target counts per bin from good_df ---
        target_counts = good_clean["_rev_bin"].value_counts().sort_index()
        avail_counts  = bad_clean_in_range["_rev_bin"].value_counts().reindex(target_counts.index, fill_value=0)

        # --- sample within each bin to match target counts ---
        matched_parts = []
        diag_rows = []

        for b in target_counts.index:
            target_n = int(target_counts.loc[b])
            candidates = bad_clean_in_range[bad_clean_in_range["_rev_bin"] == b]

            take_n = min(target_n, len(candidates))  # undersample if short
            if take_n > 0:
                matched_parts.append(candidates.sample(take_n, random_state=random_state))

            diag_rows.append({
                "bin": str(b),
                "good_count": target_n,
                "bad_available": int(len(candidates)),
                "bad_taken": int(take_n),
            })

        matched_bad = pd.concat(matched_parts, ignore_index=True) if matched_parts else bad_clean_in_range.iloc[0:0].copy()
        matched_bad = matched_bad.drop(columns=["_rev_bin"], errors="ignore")

        diagnostics = pd.DataFrame(diag_rows)
        diagnostics["shortfall"] = diagnostics["good_count"] - diagnostics["bad_taken"]
    
        return matched_bad, diagnostics

    def match_revenue_and_industry_distribution(
        self,
        good_df: pd.DataFrame,                 # reference (e.g., large users)
        bad_df: pd.DataFrame,                  # to be matched (e.g., large non-users)
        metric: str = "Revenue",
        industry_col: str = "Industry",
        quantiles=(0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0),
        random_state: int = 42,
    ):
        """
        Stratified empirical matching:
        1) Match industry mix to good_df (as many as possible)
        2) Within each industry, match metric distribution using quantile bins from good_df(industry)

        Returns:
            matched_bad_df (sampled from bad_df), diagnostics_df (industry+bin audit)
        """

        # --- basic checks / cleaning ---
        if metric not in good_df.columns or metric not in bad_df.columns:
            raise ValueError(f"'{metric}' must exist in both dfs.")
        if industry_col not in good_df.columns or industry_col not in bad_df.columns:
            raise ValueError(f"'{industry_col}' must exist in both dfs.")

        good = good_df.copy()
        bad = bad_df.copy()

        good[metric] = pd.to_numeric(good[metric], errors="coerce")
        bad[metric]  = pd.to_numeric(bad[metric], errors="coerce")

        good = good.dropna(subset=[metric, industry_col])
        bad  = bad.dropna(subset=[metric, industry_col])

        if good.empty or bad.empty:
            raise ValueError("After cleaning, one df is empty.")

        matched_parts = []
        diag_rows = []

        # target industry counts from good_df
        target_industry_counts = good[industry_col].value_counts(dropna=False)

        # iterate industry-by-industry
        for industry, target_total in target_industry_counts.items():
            good_g = good[good[industry_col] == industry]
            bad_g  = bad[bad[industry_col] == industry]

            bad_available_total = len(bad_g)
            if bad_available_total == 0:
                diag_rows.append({
                    "industry": industry,
                    "bin": None,
                    "good_count": int(target_total),
                    "bad_available": 0,
                    "bad_taken": 0,
                    "shortfall": int(target_total),
                    "note": "No bad_df rows in this industry"
                })
                continue

            # If industry is small, too many quantiles can create duplicate edges.
            # We'll compute edges and gracefully fall back to fewer bins if needed.
            qs = list(quantiles)
            edges = good_g[metric].quantile(qs).to_numpy()
            edges = np.unique(edges)

            # fallback if not enough unique cutpoints
            if len(edges) < 3:
                # try quartiles
                edges = np.unique(good_g[metric].quantile([0, 0.25, 0.5, 0.75, 1]).to_numpy())
            if len(edges) < 3:
                # last resort: just match industry count randomly (no within-industry revenue matching)
                take_n = min(int(target_total), bad_available_total)
                matched_parts.append(bad_g.sample(take_n, random_state=random_state))
                diag_rows.append({
                    "industry": industry,
                    "bin": "ALL (fallback)",
                    "good_count": int(target_total),
                    "bad_available": int(bad_available_total),
                    "bad_taken": int(take_n),
                    "shortfall": int(target_total - take_n),
                    "note": "Fallback: insufficient unique revenue values for binning"
                })
                continue

            # assign bins (from good_g edges)
            good_bins = pd.cut(good_g[metric], bins=edges, include_lowest=True)
            bad_bins  = pd.cut(bad_g[metric],  bins=edges, include_lowest=True)

            good_g = good_g.assign(_bin=good_bins)
            bad_g  = bad_g.assign(_bin=bad_bins).dropna(subset=["_bin"])  # drop outside-range

            # target counts per bin in this industry from good_df
            target_bin_counts = good_g["_bin"].value_counts().sort_index()

            # sample from bad_g within each bin
            for b, target_n in target_bin_counts.items():
                target_n = int(target_n)
                candidates = bad_g[bad_g["_bin"] == b]
                take_n = min(target_n, len(candidates))

                if take_n > 0:
                    matched_parts.append(candidates.sample(take_n, random_state=random_state))

                diag_rows.append({
                    "industry": industry,
                    "bin": str(b),
                    "good_count": target_n,
                    "bad_available": int(len(candidates)),
                    "bad_taken": int(take_n),
                    "shortfall": int(target_n - take_n),
                    "note": ""
                })

        matched_bad = (
            pd.concat(matched_parts, ignore_index=True)
            if matched_parts else bad.iloc[0:0].copy()
        )
        matched_bad = matched_bad.drop(columns=["_bin"], errors="ignore")

        diagnostics = pd.DataFrame(diag_rows)

        # Helpful overall summary rows
        overall = pd.DataFrame([{
            "industry": "ALL",
            "bin": "ALL",
            "good_count": int(len(good)),
            "bad_available": int(len(bad)),
            "bad_taken": int(len(matched_bad)),
            "shortfall": int(len(good) - len(matched_bad)),
            "note": "Overall"
        }])
        diagnostics = pd.concat([diagnostics, overall], ignore_index=True)

        return matched_bad, diagnostics


    # COUNT AND $ Amount by industry for large mkt users (PIE CHART)
    def ind_pie_data_perc(self):
        d = self.get_user(self.get_lrg_mkt(self.df))
        query = """SELECT 
                "Industry" AS sic_merge_category,
                COUNT(DISTINCT Company) AS company_count
            FROM d
            GROUP BY "Industry"
            ORDER BY company_count DESC"""
        perc_result = sqldf(query)
        query2 = """SELECT 
                    "Industry" AS sic_merge_category,
                    SUM(Revenue) AS total_revenue
                FROM d
                GROUP BY "Industry"
                ORDER BY total_revenue DESC;
""" 
        dol_result = sqldf(query2)

        # concatenate dbs
        combined = pd.concat([perc_result, dol_result], axis=1)
        print(combined)


        return combined

    
    def settle_distr(self):
        df = self.lrg_user
        s = pd.to_numeric(df["SupplierFinanceProgramObligationSettlement"], errors="coerce").dropna()

        p90 = s.quantile(0.9)
        p50 = s.quantile(0.5)

        bottom = df[df["SupplierFinanceProgramObligationSettlement"] <= p50]["SupplierFinanceProgramObligationSettlement"].sum()
        mid = df[(df["SupplierFinanceProgramObligationSettlement"] > p50) & (df["SupplierFinanceProgramObligationSettlement"] <= p90)]["SupplierFinanceProgramObligationSettlement"].sum()
        top = df[df["SupplierFinanceProgramObligationSettlement"] > p90]["SupplierFinanceProgramObligationSettlement"].sum()

        vals = [top, mid, bottom]
        labels = [
            "Top 10% ",
            "11%-50%",
            "Bottom 50%"
        ]
        total = sum(vals)
        percents = [v / total * 100 for v in vals]

        fig, ax = plt.subplots(figsize=(12, 6))


        bars = ax.bar(labels, vals, color=self.CUSTOM_BLUE_PALETTE, edgecolor="none")
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        ymax = max(vals) if vals else 0
        ax.set_ylim(0, ymax * 1.12)


        calibri = FontProperties(fname="data/calibri-regular.ttf", size=20)

        ax.set_title("Supplier Finance Program Obligation Settlement Distribution", fontsize=32, fontproperties=calibri, pad=20)
        ax.tick_params(axis="both", length=0)

        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"${x:,.0f}"))
        ax.yaxis.get_offset_text().set_visible(False)

        # Label each bar with $ value (inside) and percent of total (above)        
        for bar, v, p in zip(bars, vals, percents):
            x = bar.get_x() + bar.get_width() / 2
            h = bar.get_height()

            # above label (percent)
            ax.text(x, h + 0.03 * ymax, f"${v:,.0f} ({p:.1f}%)", ha="center", va="bottom", fontsize=11)


        output_img = "settlement_distribution.png"

        plt.savefig(
            output_img,
            dpi=300,
            bbox_inches="tight",
            facecolor="white"
        )
        plt.close()
        return output_img

        

    # <------------ TABLE 1: Top 25 Users --------------- >
    def top25_users(self, df):
        user_df = self.get_user(df)
        user_df = user_df.sort_values(by="SupplierFinanceProgramObligationSettlement", ascending=False)
        #get t25
        user_t25_df = user_df.head(25)

        #only include necessary columns
        user_tf_expt = pd.DataFrame()
        user_tf_expt['Company'] = user_t25_df['Company']
        user_tf_expt['ticker'] = user_t25_df['ticker']
        user_tf_expt['Industry'] = user_t25_df['Industry']
        user_tf_expt['AccountsPayable'] = user_t25_df['AccountsPayable']

        user_tf_expt['Revenue'] = user_t25_df['Revenue']
        user_tf_expt['CostOfRevenue'] = user_t25_df['CostOfRevenue']
        user_tf_expt['SupplierFinanceProgramObligationSettlement'] = user_t25_df['SupplierFinanceProgramObligationSettlement']
        user_tf_expt['DPO - Manual'] = user_t25_df['DPO - Manual']
        user_tf_expt['Adjusted DPO'] = user_t25_df['adjusted_DPO']

        user_tf_expt['SFP_of_COG'] = (user_tf_expt['SupplierFinanceProgramObligationSettlement'] / user_tf_expt['CostOfRevenue']) * 100

        #comparison
        rev_percent = (user_t25_df["Revenue"].sum() / user_df["Revenue"].sum()) * 100 #44.74%
        sfp_percent = (user_t25_df["SupplierFinanceProgramObligationSettlement"].sum() / user_df["SupplierFinanceProgramObligationSettlement"].sum()) * 100 #70.61%
        print(f"Top 25 Users Revenue %: {rev_percent}%")
        print(f"Top 25 Users SFP %: {sfp_percent}%")

        return user_tf_expt


    # <----------- MARKET SIZE -------------->
    def mkt_size(self, df):
        user_df = self.get_user(df)
        nusers_df = self.get_non_user(df)
        market_size = user_df["SupplierFinanceProgramObligationSettlement"].sum()
        users_count = user_df["Company"].count()
        users_revenue = user_df["Revenue"].sum()
        sfp_perc_rev = market_size / users_revenue 
        opt_sfp_perc = user_df["sfp_perc_rev"].quantile(0.75) #3rd quartile for optimal %


        non_user_count = nusers_df["Company"].count()
        non_user_revenue = nusers_df["Revenue"].sum()

        potential_mkt_size = market_size + sfp_perc_rev * non_user_revenue 
        optimal_potential_mkt_size = market_size + opt_sfp_perc * non_user_revenue


    #ACTION: MAKE AN NEW COLUMN WITH OUTLIERS AS EMPTY/NULL
    # <-------------DPO analysis------------>
    def dpo_clean(self, df):
        metric = "DPO - Manual"

        df = df.copy() 

        # 1. Force numeric
        df["DPO_clean"] = pd.to_numeric(df[metric], errors="coerce")

        # 2. Remove inf values
        df["DPO_clean"] = df["DPO_clean"].replace([np.inf, -np.inf], np.nan)

        # 3. Apply business rules
        df.loc[df["DPO_clean"] < 0, "DPO_clean"] = np.nan
        df.loc[df["DPO_clean"] > 180, "DPO_clean"] = np.nan

        # 4. (Optional but VERY helpful) validity flag
        df["DPO_valid"] = df["DPO_clean"].notna()

        # 5. Print summaries (same output as before)
        print("Users DPO:")
        print(df.loc[df["User [ 1 - yes, 0 -no]"] == 1, "DPO_clean"].describe())

        print("\nNon-users DPO:")
        print(df.loc[df["User [ 1 - yes, 0 -no]"] == 0, "DPO_clean"].describe())

        return df



    #<---------CLEANSING------------>
    def clean_ROA(self, df):
        user_df = sfp.get_user(df)
        nusers_df = sfp.get_non_user(df)

        #clean ROA data
        user_df["ROA"] = user_df["ROA"].replace([np.inf, -np.inf], np.nan) 
        user_df = user_df.dropna(subset=["ROA"])
        user_df = user_df[user_df["ROA"] < 35]

    #add a new data metric to data frame from calcbench 
    #df = dataframe to append to, metric = new metric 
    def addData(self, df, metric):

        print("********beginning calcbench data pull***********")

        try:
            cb.set_credentials("jdmathis@iu.edu", "9Cte&G}n5DTvgn")
            print("******successfully connected to calcbench*********")
        except:
            print("Cannot establish connection to calcbench")

        
        #grab tickers from df 
        tickers = df["ticker"].dropna().unique().tolist()

        print("*********Grabbing new calcbench data************")

        #grab new data 
        adj_df = cb.standardized(
            company_identifiers=tickers,
            metrics=[metric],
            fiscal_year=2024,
            fiscal_period=0,
        )

        #pivot table for formatting 
        fixed = (
            adj_df
            .pivot_table(index=["ticker"], columns="metric", values="value", aggfunc="first")
            .reset_index()
        )
        fixed.columns.name = None  

        #merge into new df 
        merge = pd.merge(df, fixed, on="ticker", how="left")

        #returns updated df 
        return merge

    def pivotAuditors(self, df):
        auditors = pd.DataFrame(df["auditor_name"])

        def normalize_auditor(name):
            if pd.isna(name):
                return None

            name = name.upper()

            if re.search(r"DELOITTE", name):
                return "Deloitte"

            if re.search(r"ERNST|YOUNG|EY", name):
                return "EY"

            if re.search(r"KPMG", name):
                return "KPMG"

            if re.search(r"PRICEWATERHOUSE|PWC", name):
                return "PwC"

            return "Other / Non-Big4"
        
        auditors["auditor_clean"] = auditors["auditor_name"].apply(normalize_auditor)

        pivot = auditors.pivot_table(aggfunc="size", index="auditor_clean", fill_value=0)

        return pivot 