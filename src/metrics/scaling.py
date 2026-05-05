import statistics
from typing import List, Optional

from src.constants import NEUTRAL_ROAS_THRESHOLD, SCALING_WINDOW_WEEKS


def compute_std_dev(weekly_pcts: List[Optional[float]], num_weeks: int = SCALING_WINDOW_WEEKS) -> dict:
    """Compute standard deviation and mean of weekly % for first N weeks.

    Args:
        weekly_pcts: List of weekly % (Week 1+, no Week 0). None values excluded.
        num_weeks: Number of weeks to analyze (default 8).

    Returns dict with: std_dev, mean_pct, num_weeks_used.
    """
    values = [p for p in weekly_pcts[:num_weeks] if p is not None]
    if len(values) < 2:
        return {"std_dev": 0.0, "mean_pct": values[0] if values else 0.0, "num_weeks_used": len(values)}

    return {
        "std_dev": statistics.stdev(values),
        "mean_pct": statistics.mean(values),
        "num_weeks_used": len(values),
    }


def _classify_relationship(spend_delta_pct: float, roas_delta_pct: float) -> str:
    """Classify the spend-ROAS relationship for a week.

    - Neutral: |ROAS Δ%| <= 2%
    - Direct: spend up AND ROAS down (normal scaling friction)
    - Inverse: spend down AND ROAS up, or both up (scaling efficiency)
    """
    if abs(roas_delta_pct) <= NEUTRAL_ROAS_THRESHOLD * 100:
        return "Neutral"
    if spend_delta_pct > 0 and roas_delta_pct < 0:
        return "Direct"
    # Inverse covers: spend down + ROAS up, or both up
    return "Inverse"


def compute_scaling_analysis(
    weekly_spend: List[Optional[float]],
    weekly_roas: List[Optional[float]],
    num_weeks: int = SCALING_WINDOW_WEEKS,
) -> List[dict]:
    """Compute spend & ROAS scaling analysis for first N weeks.

    Args:
        weekly_spend: List of weekly ad spend (Week 1+, no Week 0).
        weekly_roas: List of weekly ad ROAS (Week 1+, no Week 0).
        num_weeks: Number of weeks to analyze (default 8).

    Returns list of dicts, one per week, with:
    week, ad_spend, spend_delta_dollar, spend_delta_pct,
    ad_roas, roas_delta_x, roas_delta_pct, relationship
    """
    rows = []
    limit = min(num_weeks, len(weekly_spend), len(weekly_roas))

    for i in range(limit):
        week_num = i + 1
        spend = weekly_spend[i]
        roas = weekly_roas[i]

        if spend is None or roas is None:
            continue

        if i == 0:
            # Week 1 = baseline
            rows.append({
                "week": week_num,
                "ad_spend": spend,
                "spend_delta_dollar": None,
                "spend_delta_pct": None,
                "ad_roas": roas,
                "roas_delta_x": None,
                "roas_delta_pct": None,
                "relationship": "Baseline",
            })
        else:
            prev_spend = weekly_spend[i - 1]
            prev_roas = weekly_roas[i - 1]

            if prev_spend is None or prev_roas is None or prev_spend == 0 or prev_roas == 0:
                rows.append({
                    "week": week_num,
                    "ad_spend": spend,
                    "spend_delta_dollar": None,
                    "spend_delta_pct": None,
                    "ad_roas": roas,
                    "roas_delta_x": None,
                    "roas_delta_pct": None,
                    "relationship": None,
                })
                continue

            spend_delta_dollar = spend - prev_spend
            spend_delta_pct = (spend - prev_spend) / prev_spend * 100
            roas_delta_x = roas - prev_roas
            roas_delta_pct = (roas - prev_roas) / prev_roas * 100
            relationship = _classify_relationship(spend_delta_pct, roas_delta_pct)

            rows.append({
                "week": week_num,
                "ad_spend": spend,
                "spend_delta_dollar": spend_delta_dollar,
                "spend_delta_pct": spend_delta_pct,
                "ad_roas": roas,
                "roas_delta_x": roas_delta_x,
                "roas_delta_pct": roas_delta_pct,
                "relationship": relationship,
            })

    return rows


def compute_scaling_summary(scaling_rows: List[dict]) -> dict:
    """Compute summary statistics from scaling analysis rows.

    Returns dict with:
    - avg_spend_change_increase_dollar, avg_spend_change_increase_pct
    - avg_roas_change_increase
    - avg_spend_change_decrease_dollar, avg_spend_change_decrease_pct
    - avg_roas_change_decrease
    - increase_weeks, decrease_weeks
    """
    increase_spend_deltas = []
    increase_spend_pcts = []
    increase_roas_deltas = []
    decrease_spend_deltas = []
    decrease_spend_pcts = []
    decrease_roas_deltas = []

    for row in scaling_rows:
        if row["spend_delta_dollar"] is None:
            continue
        if row["spend_delta_dollar"] > 0:
            increase_spend_deltas.append(row["spend_delta_dollar"])
            increase_spend_pcts.append(row["spend_delta_pct"])
            increase_roas_deltas.append(row["roas_delta_x"])
        elif row["spend_delta_dollar"] < 0:
            decrease_spend_deltas.append(row["spend_delta_dollar"])
            decrease_spend_pcts.append(row["spend_delta_pct"])
            decrease_roas_deltas.append(row["roas_delta_x"])

    def _avg(lst):
        return statistics.mean(lst) if lst else 0.0

    return {
        "avg_spend_change_increase_dollar": _avg(increase_spend_deltas),
        "avg_spend_change_increase_pct": _avg(increase_spend_pcts),
        "avg_roas_change_increase": _avg(increase_roas_deltas),
        "avg_spend_change_decrease_dollar": _avg(decrease_spend_deltas),
        "avg_spend_change_decrease_pct": _avg(decrease_spend_pcts),
        "avg_roas_change_decrease": _avg(decrease_roas_deltas),
        "increase_weeks": len(increase_spend_deltas),
        "decrease_weeks": len(decrease_spend_deltas),
    }


def compute_scaling_capacity(
    total_ad_spend: float,
    total_ic_ad_spend: float,
) -> dict:
    """Compute account-level scaling capacity metrics.

    Args:
        total_ad_spend: Total ad spend across all campaigns.
        total_ic_ad_spend: Total ad spend in IC only.

    Returns dict with: duplicate_spend, duplicate_pct, ic_pct.
    """
    duplicate = total_ad_spend - total_ic_ad_spend
    return {
        "duplicate_spend": duplicate,
        "duplicate_pct": duplicate / total_ad_spend * 100 if total_ad_spend > 0 else 0.0,
        "ic_pct": total_ic_ad_spend / total_ad_spend * 100 if total_ad_spend > 0 else 0.0,
    }


def _pct_change_safe(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    """Compute percentage change, returning None if either value is None or previous is zero."""
    if current is None or previous is None or previous == 0:
        return None
    return (current - previous) / previous * 100


def compute_ad_vs_account_performance(
    account_weekly_spend: List[dict],
    account_weekly_roas: List[dict],
    num_weeks: int = SCALING_WINDOW_WEEKS,
) -> List[dict]:
    """Compute Breakthrough Ad vs Total Account Performance table.

    Uses already-computed account weekly spend/ROAS rows.
    Computes WoW delta % for ad spend, account spend, ad ROAS, account ROAS
    and classifies the relationship for the first N weeks.

    Week 0 campaign data (if present) is used as baseline to compute
    campaign-level deltas for Week 1, showing how the campaign changed
    when the ad launched.

    Args:
        account_weekly_spend: Output of compute_account_weekly_spend().
        account_weekly_roas: Output of compute_account_weekly_roas().
        num_weeks: Number of weeks to include (default 8).

    Returns list of dicts with: week, ad_spend_delta_pct, account_spend_delta_pct,
    ad_roas_delta_pct, account_roas_delta_pct, relationship.
    """
    # Extract Week 0 campaign data for baseline (ad doesn't exist yet)
    wk0_spend = next((r for r in account_weekly_spend if r["week"] == 0), None)
    wk0_roas = next((r for r in account_weekly_roas if r["week"] == 0), None)
    wk0_account_spend = wk0_spend["account_spend"] if wk0_spend else None
    wk0_account_roas = wk0_roas["account_roas"] if wk0_roas else None

    spend_rows = [r for r in account_weekly_spend if r["week"] > 0][:num_weeks]
    roas_rows = [r for r in account_weekly_roas if r["week"] > 0][:num_weeks]

    rows = []
    prev_ad_spend = None
    prev_account_spend = None
    prev_ad_roas = None
    prev_account_roas = None

    for i in range(min(len(spend_rows), len(roas_rows))):
        week_num = spend_rows[i]["week"]
        ad_spend = spend_rows[i]["ad_spend"]
        account_spend = spend_rows[i]["account_spend"]
        ad_roas = roas_rows[i]["ad_roas"]
        account_roas = roas_rows[i]["account_roas"]

        if i == 0:
            # Week 1: ad deltas are None (Baseline), but campaign deltas
            # show the Week 0 → Week 1 change if Week 0 data exists
            account_spend_delta = _pct_change_safe(account_spend, wk0_account_spend)
            account_roas_delta = _pct_change_safe(account_roas, wk0_account_roas)
            rows.append({
                "week": week_num,
                "ad_spend_delta_pct": None,
                "account_spend_delta_pct": account_spend_delta,
                "ad_roas_delta_pct": None,
                "account_roas_delta_pct": account_roas_delta,
                "relationship": "Baseline",
            })
        else:
            ad_spend_delta = _pct_change_safe(ad_spend, prev_ad_spend)
            account_spend_delta = _pct_change_safe(account_spend, prev_account_spend)
            ad_roas_delta = _pct_change_safe(ad_roas, prev_ad_roas)
            account_roas_delta = _pct_change_safe(account_roas, prev_account_roas)

            relationship = None
            if ad_spend_delta is not None and ad_roas_delta is not None:
                relationship = _classify_relationship(ad_spend_delta, ad_roas_delta)

            rows.append({
                "week": week_num,
                "ad_spend_delta_pct": ad_spend_delta,
                "account_spend_delta_pct": account_spend_delta,
                "ad_roas_delta_pct": ad_roas_delta,
                "account_roas_delta_pct": account_roas_delta,
                "relationship": relationship,
            })

        prev_ad_spend = ad_spend
        prev_account_spend = account_spend
        prev_ad_roas = ad_roas
        prev_account_roas = account_roas

    return rows


def compute_ad_vs_ic_performance(
    ic_weekly_spend: List[dict],
    ic_weekly_roas: List[dict],
    num_weeks: int = SCALING_WINDOW_WEEKS,
) -> List[dict]:
    """Compute Breakthrough Ad vs Initial Campaign Performance table.

    Uses already-computed IC weekly spend/ROAS rows.
    Computes WoW delta % for ad spend, IC total spend, ad ROAS, IC total ROAS
    and classifies the relationship for the first N weeks.

    Week 0 campaign data (if present) is used as baseline to compute
    campaign-level deltas for Week 1, showing how the campaign changed
    when the ad launched.

    Args:
        ic_weekly_spend: Output of compute_ic_weekly_spend().
        ic_weekly_roas: Output of compute_ic_weekly_roas().
        num_weeks: Number of weeks to include (default 8).

    Returns list of dicts with: week, ad_spend_delta_pct, ic_spend_delta_pct,
    ad_roas_delta_pct, ic_roas_delta_pct, relationship.
    """
    # Extract Week 0 campaign data for baseline (ad doesn't exist yet)
    wk0_spend = next((r for r in ic_weekly_spend if r["week"] == 0), None)
    wk0_roas = next((r for r in ic_weekly_roas if r["week"] == 0), None)
    wk0_ic_spend = wk0_spend["total_spend"] if wk0_spend else None
    wk0_ic_roas = wk0_roas["total_roas"] if wk0_roas else None

    spend_rows = [r for r in ic_weekly_spend if r["week"] > 0][:num_weeks]
    roas_rows = [r for r in ic_weekly_roas if r["week"] > 0][:num_weeks]

    rows = []
    prev_ad_spend = None
    prev_ic_spend = None
    prev_ad_roas = None
    prev_ic_roas = None

    for i in range(min(len(spend_rows), len(roas_rows))):
        week_num = spend_rows[i]["week"]
        ad_spend = spend_rows[i]["ad_spend"]
        ic_spend = spend_rows[i]["total_spend"]
        ad_roas = roas_rows[i]["ad_roas"]
        ic_roas = roas_rows[i]["total_roas"]

        if i == 0:
            # Week 1: ad deltas are None (Baseline), but campaign deltas
            # show the Week 0 → Week 1 change if Week 0 data exists
            ic_spend_delta = _pct_change_safe(ic_spend, wk0_ic_spend)
            ic_roas_delta = _pct_change_safe(ic_roas, wk0_ic_roas)
            rows.append({
                "week": week_num,
                "ad_spend_delta_pct": None,
                "ic_spend_delta_pct": ic_spend_delta,
                "ad_roas_delta_pct": None,
                "ic_roas_delta_pct": ic_roas_delta,
                "relationship": "Baseline",
            })
        else:
            ad_spend_delta = _pct_change_safe(ad_spend, prev_ad_spend)
            ic_spend_delta = _pct_change_safe(ic_spend, prev_ic_spend)
            ad_roas_delta = _pct_change_safe(ad_roas, prev_ad_roas)
            ic_roas_delta = _pct_change_safe(ic_roas, prev_ic_roas)

            relationship = None
            if ad_spend_delta is not None and ad_roas_delta is not None:
                relationship = _classify_relationship(ad_spend_delta, ad_roas_delta)

            rows.append({
                "week": week_num,
                "ad_spend_delta_pct": ad_spend_delta,
                "ic_spend_delta_pct": ic_spend_delta,
                "ad_roas_delta_pct": ad_roas_delta,
                "ic_roas_delta_pct": ic_roas_delta,
                "relationship": relationship,
            })

        prev_ad_spend = ad_spend
        prev_ic_spend = ic_spend
        prev_ad_roas = ad_roas
        prev_ic_roas = ic_roas

    return rows
