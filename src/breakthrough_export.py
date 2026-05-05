"""Export single-ad breakthrough data as a single-tab stacked CSV."""

import csv
import os
from datetime import date
from typing import List, Optional

from src.csv_parser import load_csv
from src.data_prep import prepare
from src.metrics.overview import compute_ic_overview, compute_account_overview
from src.metrics.weekly import (
    compute_ic_weekly_spend,
    compute_ic_weekly_roas,
    compute_account_weekly_spend,
    compute_account_weekly_roas,
)

# Weeks 0-8 (9 entries)
WEEKS = 9

# Spend tier thresholds (monthly avg)
TIER_THRESHOLDS = [
    (100_000, "$0-100K/month"),
    (250_000, "$100K-250K/month"),
    (500_000, "$250K-500K/month"),
    (float("inf"), "$500K+/month"),
]


def _determine_tier(total_spend: float, months: int) -> str:
    """Map monthly average spend to a tier label."""
    monthly_avg = total_spend / max(months, 1)
    for threshold, label in TIER_THRESHOLDS:
        if monthly_avg < threshold:
            return label
    return TIER_THRESHOLDS[-1][1]


def _pad_weekly(rows: List[dict], total: int = WEEKS) -> List[dict]:
    """Ensure exactly `total` weekly entries (Week 0 through Week total-1)."""
    result = rows[:total]
    if len(result) < total:
        existing_weeks = {r["week"] for r in result}
        for w in range(total):
            if w not in existing_weeks:
                result.append({"week": w})
        result.sort(key=lambda r: r["week"])
    return result


def _fmt(val, decimals=2):
    """Format a value for CSV. None → empty string."""
    if val is None:
        return ""
    if isinstance(val, float):
        return round(val, decimals)
    return val


def _compute_wow(rows: List[dict], spend_key: str) -> List[Optional[float]]:
    """Compute week-over-week % change for a spend column."""
    result = [None]  # Week 0 is always None
    for i in range(1, len(rows)):
        prev = rows[i - 1].get(spend_key)
        curr = rows[i].get(spend_key)
        if prev and prev > 0 and curr is not None:
            result.append(((curr - prev) / prev) * 100)
        else:
            result.append(None)
    return result


def generate_breakthrough_csv(
    csv_path: str,
    creative_name: str,
    brand_name: str,
    ic_campaign: Optional[str] = None,
    output_dir: str = "breakthrough-reports",
) -> str:
    """Generate a single-tab stacked CSV for one breakthrough ad.

    Args:
        csv_path: Path to Meta Ads Manager CSV export.
        creative_name: Creative identifier (substring match, case-insensitive).
        brand_name: Brand/account name for the report header.
        ic_campaign: Optional IC campaign override.
        output_dir: Directory to write the output CSV.

    Returns:
        Path to the written CSV file.
    """
    # 1. Load and prepare
    parsed = load_csv(csv_path)
    p = prepare(
        parsed.df,
        creative_name,
        parsed.analysis_period,
        ic_campaign=ic_campaign,
        case_sensitive=False,
    )

    # 2. Compute spend tier
    total_account_spend = parsed.df["amount_spent"].sum()
    period_start = parsed.analysis_period.start
    period_end = parsed.analysis_period.end
    months = max(1, (period_end.year - period_start.year) * 12 + (period_end.month - period_start.month))
    tier = _determine_tier(total_account_spend, months)

    # 3. Compute weekly metrics
    ic_wk_spend = _pad_weekly(compute_ic_weekly_spend(p.ad_ic_df, p.ic_df, p.weekly_periods))
    ic_wk_roas = _pad_weekly(compute_ic_weekly_roas(p.ad_ic_df, p.ic_df, p.weekly_periods))
    acct_wk_spend = _pad_weekly(compute_account_weekly_spend(p.ad_all_df, p.ad_ic_df, p.account_df, p.weekly_periods))
    acct_wk_roas = _pad_weekly(compute_account_weekly_roas(p.ad_all_df, p.ad_ic_df, p.account_df, p.weekly_periods))

    # 4. Compute WoW deltas
    ic_spend_wow = _compute_wow(ic_wk_spend, "total_spend")
    acct_spend_wow = _compute_wow(acct_wk_spend, "account_spend")

    # 5. Build output
    os.makedirs(output_dir, exist_ok=True)
    clean_brand = brand_name.replace(" ", "_")
    clean_creative = creative_name.replace(" ", "_").replace("#", "").replace("/", "_")
    filename = f"{clean_brand}_{clean_creative}_{date.today().isoformat()}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        # Header metadata
        writer.writerow(["Brand", brand_name])
        writer.writerow(["Ad", creative_name])
        writer.writerow(["Account Tier", tier])
        writer.writerow(["IC Campaign", p.ic_campaign_name])
        writer.writerow(["Analysis Period", f"{period_start} to {period_end}"])
        writer.writerow([])

        # --- IC WEEKLY SPEND ---
        writer.writerow(["--- IC WEEKLY SPEND ---"])
        writer.writerow(["Week", "Ad % of Campaign", "Ad $", "IC $", "IC Spend WoW Δ%"])
        for i, row in enumerate(ic_wk_spend):
            writer.writerow([
                row["week"],
                _fmt(row.get("pct_of_campaign")),
                _fmt(row.get("ad_spend")),
                _fmt(row.get("total_spend")),
                _fmt(ic_spend_wow[i]),
            ])
        writer.writerow([])

        # --- IC WEEKLY ROAS ---
        writer.writerow(["--- IC WEEKLY ROAS ---"])
        writer.writerow(["Week", "Ad % vs Campaign"])
        for row in ic_wk_roas:
            writer.writerow([
                row["week"],
                _fmt(row.get("pct_vs_campaign")),
            ])
        writer.writerow([])

        # --- ACCOUNT WEEKLY SPEND ---
        writer.writerow(["--- ACCOUNT WEEKLY SPEND ---"])
        writer.writerow(["Week", "Ad % of Account", "Ad $", "Account $", "Account Spend WoW Δ%"])
        for i, row in enumerate(acct_wk_spend):
            writer.writerow([
                row["week"],
                _fmt(row.get("pct_of_account")),
                _fmt(row.get("ad_spend")),
                _fmt(row.get("account_spend")),
                _fmt(acct_spend_wow[i]),
            ])
        writer.writerow([])

        # --- ACCOUNT WEEKLY ROAS ---
        writer.writerow(["--- ACCOUNT WEEKLY ROAS ---"])
        writer.writerow(["Week", "Ad % vs Account"])
        for row in acct_wk_roas:
            writer.writerow([
                row["week"],
                _fmt(row.get("pct_vs_account")),
            ])

    return filepath
