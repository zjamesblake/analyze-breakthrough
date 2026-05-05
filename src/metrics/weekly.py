from datetime import date
from typing import List, Optional, Tuple

import pandas as pd


def _period_agg(df: pd.DataFrame, start: date, end: date) -> dict:
    """Aggregate spend, purchases, revenue for a date range."""
    rows = df[(df["day"] >= start) & (df["day"] <= end)]
    return {
        "spend": rows["amount_spent"].sum(),
        "purchases": int(rows["purchases"].sum()),
        "revenue": rows["purchase_conversion_value"].sum(),
    }


def _pct_change(current: float, previous: float) -> Optional[float]:
    """Compute percentage change: (current - previous) / previous * 100."""
    if previous > 0:
        return (current - previous) / previous * 100
    return None


def _roas(spend: float, revenue: float) -> float:
    """Compute ROAS from spend and revenue."""
    return revenue / spend if spend > 0 else 0.0


def compute_ic_weekly_spend(
    ad_ic_df: pd.DataFrame,
    ic_df: pd.DataFrame,
    weekly_periods: List[Tuple[int, date, date]],
) -> List[dict]:
    """Compute IC Weekly Spend table (Section 1.4).

    Returns list of dicts with: week, period, ad_spend, total_spend,
    pct_of_campaign, ad_vs_prev, total_vs_prev, total_vs_wk0
    """
    rows = []
    prev_ad_spend = None
    prev_total_spend = None
    wk0_total_spend = None

    for week_num, start, end in weekly_periods:
        ad = _period_agg(ad_ic_df, start, end)
        total = _period_agg(ic_df, start, end)
        period_str = f"{start.strftime('%b %d')} - {end.strftime('%b %d')}"

        is_week0 = week_num == 0

        # Week 0: ad hasn't launched yet
        ad_spend = None if is_week0 else ad["spend"]
        pct_of_campaign = None if is_week0 else (
            ad["spend"] / total["spend"] * 100 if total["spend"] > 0 else 0.0
        )

        # % vs prev
        ad_vs_prev = None
        if not is_week0 and prev_ad_spend is not None:
            ad_vs_prev = _pct_change(ad["spend"], prev_ad_spend)

        total_vs_prev = None
        if prev_total_spend is not None:
            total_vs_prev = _pct_change(total["spend"], prev_total_spend)

        # % vs Wk0
        total_vs_wk0 = None
        if not is_week0 and wk0_total_spend is not None:
            total_vs_wk0 = _pct_change(total["spend"], wk0_total_spend)

        rows.append({
            "week": week_num,
            "period": period_str,
            "ad_spend": ad_spend,
            "total_spend": total["spend"],
            "pct_of_campaign": pct_of_campaign,
            "ad_vs_prev": ad_vs_prev,
            "total_vs_prev": total_vs_prev,
            "total_vs_wk0": total_vs_wk0,
        })

        if is_week0:
            wk0_total_spend = total["spend"]
        else:
            prev_ad_spend = ad["spend"]
        prev_total_spend = total["spend"]

    return rows


def compute_ic_weekly_roas(
    ad_ic_df: pd.DataFrame,
    ic_df: pd.DataFrame,
    weekly_periods: List[Tuple[int, date, date]],
) -> List[dict]:
    """Compute IC Weekly ROAS table (Section 1.5).

    Returns list of dicts with: week, ad_roas, total_roas,
    pct_vs_campaign, ad_roas_vs_prev, total_roas_vs_prev
    """
    rows = []
    prev_ad_roas = None
    prev_total_roas = None

    for week_num, start, end in weekly_periods:
        ad = _period_agg(ad_ic_df, start, end)
        total = _period_agg(ic_df, start, end)

        is_week0 = week_num == 0
        ad_roas = None if is_week0 else _roas(ad["spend"], ad["revenue"])
        total_roas = _roas(total["spend"], total["revenue"])

        pct_vs_campaign = None
        if not is_week0 and total_roas > 0:
            pct_vs_campaign = (ad_roas / total_roas - 1) * 100

        ad_roas_vs_prev = None
        if not is_week0 and prev_ad_roas is not None and prev_ad_roas > 0:
            ad_roas_vs_prev = _pct_change(ad_roas, prev_ad_roas)

        total_roas_vs_prev = None
        if prev_total_roas is not None and prev_total_roas > 0:
            total_roas_vs_prev = _pct_change(total_roas, prev_total_roas)

        rows.append({
            "week": week_num,
            "ad_roas": ad_roas,
            "total_roas": total_roas,
            "pct_vs_campaign": pct_vs_campaign,
            "ad_roas_vs_prev": ad_roas_vs_prev,
            "total_roas_vs_prev": total_roas_vs_prev,
        })

        if not is_week0:
            prev_ad_roas = ad_roas
        prev_total_roas = total_roas

    return rows


def compute_account_weekly_spend(
    ad_all_df: pd.DataFrame,
    ad_ic_df: pd.DataFrame,
    account_df: pd.DataFrame,
    weekly_periods: List[Tuple[int, date, date]],
) -> List[dict]:
    """Compute Account Weekly Spend table (Section 2.4).

    Returns list of dicts with: week, period, ad_spend, account_spend,
    duplicate_spend, pct_of_account, ad_vs_prev, account_vs_prev, account_vs_wk0
    """
    rows = []
    prev_ad_spend = None
    prev_account_spend = None
    wk0_account_spend = None

    for week_num, start, end in weekly_periods:
        ad_all = _period_agg(ad_all_df, start, end)
        ad_ic = _period_agg(ad_ic_df, start, end)
        acct = _period_agg(account_df, start, end)
        period_str = f"{start.strftime('%b %d')} - {end.strftime('%b %d')}"

        is_week0 = week_num == 0
        ad_spend = None if is_week0 else ad_all["spend"]
        dup_spend = None if is_week0 else ad_all["spend"] - ad_ic["spend"]
        pct_of_account = None if is_week0 else (
            ad_all["spend"] / acct["spend"] * 100 if acct["spend"] > 0 else 0.0
        )

        ad_vs_prev = None
        if not is_week0 and prev_ad_spend is not None:
            ad_vs_prev = _pct_change(ad_all["spend"], prev_ad_spend)

        account_vs_prev = None
        if prev_account_spend is not None:
            account_vs_prev = _pct_change(acct["spend"], prev_account_spend)

        account_vs_wk0 = None
        if not is_week0 and wk0_account_spend is not None:
            account_vs_wk0 = _pct_change(acct["spend"], wk0_account_spend)

        rows.append({
            "week": week_num,
            "period": period_str,
            "ad_spend": ad_spend,
            "account_spend": acct["spend"],
            "duplicate_spend": dup_spend,
            "pct_of_account": pct_of_account,
            "ad_vs_prev": ad_vs_prev,
            "account_vs_prev": account_vs_prev,
            "account_vs_wk0": account_vs_wk0,
        })

        if is_week0:
            wk0_account_spend = acct["spend"]
        else:
            prev_ad_spend = ad_all["spend"]
        prev_account_spend = acct["spend"]

    return rows


def compute_account_weekly_roas(
    ad_all_df: pd.DataFrame,
    ad_ic_df: pd.DataFrame,
    account_df: pd.DataFrame,
    weekly_periods: List[Tuple[int, date, date]],
) -> List[dict]:
    """Compute Account Weekly ROAS table (Section 2.5).

    Returns list of dicts with: week, ad_roas, ic_ad_roas, account_roas,
    pct_vs_account, ad_roas_vs_prev, account_roas_vs_prev
    """
    rows = []
    prev_ad_roas = None
    prev_account_roas = None

    for week_num, start, end in weekly_periods:
        ad_all = _period_agg(ad_all_df, start, end)
        ad_ic = _period_agg(ad_ic_df, start, end)
        acct = _period_agg(account_df, start, end)

        is_week0 = week_num == 0
        ad_roas = None if is_week0 else _roas(ad_all["spend"], ad_all["revenue"])
        ic_ad_roas = None if is_week0 else _roas(ad_ic["spend"], ad_ic["revenue"])
        account_roas = _roas(acct["spend"], acct["revenue"])

        pct_vs_account = None
        if not is_week0 and account_roas > 0:
            pct_vs_account = (ad_roas / account_roas - 1) * 100

        ad_roas_vs_prev = None
        if not is_week0 and prev_ad_roas is not None and prev_ad_roas > 0:
            ad_roas_vs_prev = _pct_change(ad_roas, prev_ad_roas)

        account_roas_vs_prev = None
        if prev_account_roas is not None and prev_account_roas > 0:
            account_roas_vs_prev = _pct_change(account_roas, prev_account_roas)

        rows.append({
            "week": week_num,
            "ad_roas": ad_roas,
            "ic_ad_roas": ic_ad_roas,
            "account_roas": account_roas,
            "pct_vs_account": pct_vs_account,
            "ad_roas_vs_prev": ad_roas_vs_prev,
            "account_roas_vs_prev": account_roas_vs_prev,
        })

        if not is_week0:
            prev_ad_roas = ad_roas
        prev_account_roas = account_roas

    return rows
