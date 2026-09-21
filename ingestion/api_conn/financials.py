from __future__ import annotations

import calcbench as cb
import pandas as pd

from client import initialize_calcbench
from collections.abc import Sequence


def pull_standardized_financials(
    company_identifiers: Sequence[str | int],
    metrics: Sequence[str],
    fiscal_year: int,
    fiscal_period: int = 0,
    point_in_time: bool = False,
    xbrl_only: bool = False,
) -> pd.DataFrame:
    """
    Pull standardized Calcbench financial data for one fiscal year.

    Parameters
    ----------
    company_identifiers : Sequence[str | int]
        Company tickers or CIKs.

    metrics : Sequence[str]
        Calcbench standardized metric names.

    fiscal_year : int
        Fiscal year to retrieve.

    fiscal_period : int, default=0
        Fiscal period:
            0 = annual

    point_in_time : bool, default=False
        If True, return Calcbench revision / filing metadata.

    xbrl_only : bool, default=False
        If True, restrict results to values that appeared in XBRL.

    Returns
    -------
    pd.DataFrame
        Calcbench standardized numeric data.
    """

    if not company_identifiers:
        raise ValueError("company_identifiers cannot be empty.")

    if not metrics:
        raise ValueError("metrics cannot be empty.")

    cb = initialize_calcbench()

    df = cb.standardized(
        company_identifiers=list(company_identifiers),
        metrics=list(metrics),
        fiscal_year=fiscal_year,
        fiscal_period=fiscal_period,
        point_in_time=point_in_time,
        XBRL_only=xbrl_only,
    )

    if df is None:
        return pd.DataFrame()

    return df.reset_index(drop=True)


def pull_financials_for_years(
    company_identifiers: Sequence[str | int],
    metrics: Sequence[str],
    fiscal_years: Sequence[int],
    fiscal_period: int = 0,
    point_in_time: bool = False,
    xbrl_only: bool = False,
) -> pd.DataFrame:
    """
    Pull standardized financial data across multiple fiscal years.

    Calcbench's standardized() function accepts a single fiscal_year,
    so this function loops through the requested years and combines
    the results.

    Returns
    -------
    pd.DataFrame
        Combined standardized Calcbench data.
    """

    results = []

    for fiscal_year in fiscal_years:

        df = pull_standardized_financials(
            company_identifiers=company_identifiers,
            metrics=metrics,
            fiscal_year=fiscal_year,
            fiscal_period=fiscal_period,
            point_in_time=point_in_time,
            xbrl_only=xbrl_only,
        )

        if not df.empty:
            results.append(df)

    if not results:
        return pd.DataFrame()

    return pd.concat(
        results,
        ignore_index=True,
    )


def pull_financials_batched(
    company_identifiers: Sequence[str | int],
    metrics: Sequence[str],
    fiscal_years: Sequence[int],
    batch_size: int = 100,
    fiscal_period: int = 0,
    point_in_time: bool = False,
    xbrl_only: bool = False,
) -> pd.DataFrame:
    """
    Pull standardized Calcbench financials in company batches.

    This is intended for larger ingestion jobs so that one API request
    does not contain the entire company universe.

    Parameters
    ----------
    company_identifiers : Sequence[str | int]
        Tickers and/or CIKs.

    metrics : Sequence[str]
        Calcbench standardized metric names.

    fiscal_years : Sequence[int]
        Fiscal years to retrieve.

    batch_size : int, default=100
        Number of companies to send in each batch.

    fiscal_period : int, default=0
        0 for annual observations.

    point_in_time : bool, default=False
        Include revision and filing metadata.

    xbrl_only : bool, default=False
        Restrict results to XBRL observations.

    Returns
    -------
    pd.DataFrame
        Combined standardized financial data.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0.")

    companies = list(company_identifiers)

    results = []

    for start in range(0, len(companies), batch_size):

        batch = companies[start : start + batch_size]

        df = pull_financials_for_years(
            company_identifiers=batch,
            metrics=metrics,
            fiscal_years=fiscal_years,
            fiscal_period=fiscal_period,
            point_in_time=point_in_time,
            xbrl_only=xbrl_only,
        )

        if not df.empty:
            results.append(df)

    if not results:
        return pd.DataFrame()

    return pd.concat(
        results,
        ignore_index=True,
    )