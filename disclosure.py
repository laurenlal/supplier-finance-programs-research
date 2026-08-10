import pandas as pd
import re
import numpy as np



def categorize_program(text):
    """Return classification: AP, Debt, Hybrid, or Unknown."""
    t = text.lower()

    # Debt-like indicators
    debt_terms = [
        "debt", "borrowing", "short-term borrowing", "financing arrangement",
        "notes payable", "interest-bearing", "secured", "bank", "credit facility",
        "loan", "collateral"
    ]

    # AP-like indicators
    ap_terms = [
        "accounts payable", "trade payable", "extended terms", 
        "payment terms", "supply chain finance", "reverse factoring",
        "obligation to suppliers"
    ]

    debt_score = sum(1 for w in debt_terms if w in t)
    ap_score = sum(1 for w in ap_terms if w in t)

    if debt_score == 0 and ap_score == 0:
        return "Unknown"

    if debt_score > 0 and ap_score > 0:
        return "Hybrid / Ambiguous"

    return "Debt" if debt_score > ap_score else "Accounts Payable"


def extract_payment_terms(text):
    """
    Scan text for phrases like '60 days', 'net 60', '60-90 days', etc.
    Returns a bucket for standardized terms.
    """
    t = text.lower()

    # Find any numeric terms like 30, 45, 60, 90, 120, etc.
    matches = re.findall(r"(\d{2,3})\s*(?:day|days|d)", t)
    ranges = re.findall(r"(\d{2,3})\s*-\s*(\d{2,3})\s*days", t)

    # Priority: explicit ranges first
    if ranges:
        low, high = map(int, ranges[0])
        avg = (low + high) / 2
    elif matches:
        nums = [int(x) for x in matches]
        avg = np.mean(nums)
    else:
        return "Not disclosed"

    # Bucket into categories
    if avg < 45:
        return "<45 days"
    elif 45 <= avg <= 60:
        return "45–60 days"
    elif 60 < avg <= 90:
        return "60–90 days"
    elif 90 < avg <= 120:
        return "90–120 days"
    else:
        return "120+ days"



def parse_sfp_disclosures(input_file, text_column="Disclosure", output_file="parsed_results.csv"):
    """
    input_file: path to Excel/CSV file
    text_column: name of the column containing disclosure text
    """

    print(f"Loading file: {input_file}")

    if input_file.endswith(".csv"):
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)

    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in file. Columns available: {df.columns}")

    # Apply classifiers
    df["SFP_Category"] = df[text_column].astype(str).apply(categorize_program)
    df["Payment_Terms"] = df[text_column].astype(str).apply(extract_payment_terms)

    # Save output
    df.to_csv(output_file, index=False)
    print(f"Saved parsed results → {output_file}")

    return df

# -----------------------------------------
# Example usage
# -----------------------------------------

if __name__ == "__main__":
    results = parse_sfp_disclosures("sfp_disclosures.xlsx", text_column="Disclosure")
    print(results.head())
