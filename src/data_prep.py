from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Tuple

import pandas as pd

from src.ad_name_parser import AdMetadata, parse_ad_name
from src.csv_parser import AnalysisPeriod


@dataclass
class PreparedData:
    creative_name: str  # "BATCH#61"
    ad_metadata: AdMetadata  # Parsed from first matching ad name
    launch_date: date  # Earliest date the creative appears
    ic_campaign_name: str  # IC campaign name
    analysis_start: date  # From CSV summary row
    analysis_end: date  # From CSV summary row

    ad_ic_df: pd.DataFrame  # Ad rows in IC campaign only
    ad_all_df: pd.DataFrame  # Ad rows across ALL campaigns
    ic_df: pd.DataFrame  # ALL rows in IC campaign (all ads)
    account_df: pd.DataFrame  # ALL rows in account (full CSV minus summary)

    weekly_periods: List[Tuple[int, date, date]]  # [(week_num, start, end), ...]
    variations_count: int  # Number of distinct campaigns containing the ad
    variation_names: List[str]  # Campaign names containing the ad


def match_creative(df: pd.DataFrame, creative_name: str, case_sensitive: bool = True) -> pd.DataFrame:
    """Find all rows where creative_name appears in ad_name (substring match)."""
    mask = df["ad_name"].str.contains(creative_name, case=case_sensitive, na=False, regex=False)
    return df[mask].copy()


def determine_ic(ad_df: pd.DataFrame) -> str:
    """Determine the Initial Campaign (IC) — the campaign where the creative first appeared.

    Tiebreaker: if the creative appears in multiple campaigns on its earliest date,
    pick the campaign with the highest combined (spend + purchases).
    """
    earliest_date = ad_df["day"].min()
    first_day_rows = ad_df[ad_df["day"] == earliest_date]

    if first_day_rows["campaign_name"].nunique() == 1:
        return first_day_rows["campaign_name"].iloc[0]

    # Tiebreaker: most spend + purchases
    by_campaign = first_day_rows.groupby("campaign_name").agg(
        total_spend=("amount_spent", "sum"),
        total_purchases=("purchases", "sum"),
    )
    by_campaign["score"] = by_campaign["total_spend"] + by_campaign["total_purchases"]
    return by_campaign["score"].idxmax()


def generate_weekly_periods(
    launch_date: date, analysis_end: date
) -> List[Tuple[int, date, date]]:
    """Generate launch-date-aligned 7-day periods.

    Week 0: 7 days before launch (launch_date - 7 to launch_date - 1)
    Week 1: launch_date to launch_date + 6
    Week N: continues in 7-day blocks through end of analysis period
    """
    periods = []

    # Week 0: 7 days before launch
    wk0_start = launch_date - timedelta(days=7)
    wk0_end = launch_date - timedelta(days=1)
    periods.append((0, wk0_start, wk0_end))

    # Week 1+: 7-day windows from launch date
    week_num = 1
    wk_start = launch_date
    while wk_start <= analysis_end:
        wk_end = min(wk_start + timedelta(days=6), analysis_end)
        periods.append((week_num, wk_start, wk_end))
        week_num += 1
        wk_start = wk_start + timedelta(days=7)

    return periods


def prepare(
    df: pd.DataFrame,
    creative_name: str,
    analysis_period: AnalysisPeriod,
    ic_campaign: Optional[str] = None,
    case_sensitive: bool = True,
) -> PreparedData:
    """Orchestrate data preparation for a given creative.

    Takes the full account DataFrame (from csv_parser), a creative name,
    and the analysis period. Returns PreparedData with all filtered
    DataFrames and metadata needed by the metrics engine.

    Args:
        ic_campaign: Optional IC campaign name override. When provided,
            uses this campaign as the IC instead of auto-detecting via
            earliest date. Launch date is set to the creative's first
            appearance in the specified campaign.
        case_sensitive: Whether creative name matching is case-sensitive
            (default True). Set False when ad names have inconsistent casing.
    """
    # Match all rows for this creative
    ad_all_df = match_creative(df, creative_name, case_sensitive=case_sensitive)
    if ad_all_df.empty:
        raise ValueError(f"No rows found matching creative '{creative_name}'")

    # Parse metadata from the first matching ad name
    first_ad_name = ad_all_df["ad_name"].iloc[0]
    ad_metadata = parse_ad_name(first_ad_name)

    # Determine IC and launch date
    if ic_campaign:
        ic_campaign_name = ic_campaign
        ic_rows = ad_all_df[ad_all_df["campaign_name"] == ic_campaign]
        if ic_rows.empty:
            raise ValueError(
                f"IC override campaign '{ic_campaign}' has no rows for "
                f"creative '{creative_name}'"
            )
        launch_date = ic_rows["day"].min()
    else:
        ic_campaign_name = determine_ic(ad_all_df)
        launch_date = ad_all_df["day"].min()

    # Filter DataFrames
    ad_ic_df = ad_all_df[ad_all_df["campaign_name"] == ic_campaign_name].copy()
    ic_df = df[df["campaign_name"] == ic_campaign_name].copy()
    account_df = df  # full CSV (already has summary row removed by csv_parser)

    # Generate weekly periods
    weekly_periods = generate_weekly_periods(launch_date, analysis_period.end)

    # Count variations (distinct campaigns containing the ad)
    variation_names = sorted(ad_all_df["campaign_name"].unique().tolist())
    variations_count = len(variation_names)

    return PreparedData(
        creative_name=creative_name,
        ad_metadata=ad_metadata,
        launch_date=launch_date,
        ic_campaign_name=ic_campaign_name,
        analysis_start=analysis_period.start,
        analysis_end=analysis_period.end,
        ad_ic_df=ad_ic_df,
        ad_all_df=ad_all_df,
        ic_df=ic_df,
        account_df=account_df,
        weekly_periods=weekly_periods,
        variations_count=variations_count,
        variation_names=variation_names,
    )
