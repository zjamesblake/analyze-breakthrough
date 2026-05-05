from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.constants import COLUMN_RENAME_MAP


@dataclass
class AnalysisPeriod:
    """Reporting period extracted from the CSV summary row."""

    start: date
    end: date


@dataclass
class ParsedCSV:
    """Result of parsing a Meta Ads Manager CSV export."""

    df: pd.DataFrame
    analysis_period: AnalysisPeriod


def load_csv(file_path: str) -> ParsedCSV:
    """Load a Meta Ads Manager CSV export.

    - Reads the CSV
    - Renames columns to canonical names
    - Extracts the analysis period from the summary row
    - Removes the summary row
    - Converts column types and fills NaN values
    """
    raw = pd.read_csv(file_path)

    # Rename columns to canonical names
    raw = raw.rename(columns=COLUMN_RENAME_MAP)

    # Identify summary row: campaign_name is NaN
    summary_mask = raw["campaign_name"].isna()
    summary_rows = raw[summary_mask]

    if summary_rows.empty:
        raise ValueError("No summary row found (expected a row with empty campaign_name)")

    summary = summary_rows.iloc[0]

    # Extract analysis period from summary row
    analysis_period = AnalysisPeriod(
        start=pd.to_datetime(summary["reporting_starts"]).date(),
        end=pd.to_datetime(summary["reporting_ends"]).date(),
    )

    # Remove summary row(s)
    df = raw[~summary_mask].copy()

    # Type conversions
    df["day"] = pd.to_datetime(df["day"]).dt.date
    df["reporting_starts"] = pd.to_datetime(df["reporting_starts"]).dt.date
    df["reporting_ends"] = pd.to_datetime(df["reporting_ends"]).dt.date

    df["amount_spent"] = df["amount_spent"].astype(float)
    df["roas"] = df["roas"].astype(float)

    # Fill NaN and convert
    df["purchases"] = df["purchases"].fillna(0).astype(int)
    df["cost_per_purchase"] = df["cost_per_purchase"].fillna(0.0).astype(float)
    df["purchase_conversion_value"] = df["purchase_conversion_value"].fillna(0.0).astype(float)

    # Reset index after dropping summary row
    df = df.reset_index(drop=True)

    return ParsedCSV(df=df, analysis_period=analysis_period)
