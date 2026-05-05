from datetime import date, timedelta

import pandas as pd


def compute_ic_overview(
    ad_ic_df: pd.DataFrame,
    ic_df: pd.DataFrame,
    launch_date: date,
    analysis_end: date,
) -> dict:
    """Compute IC Overview metrics (Section 1.1).

    All percentages are calculated from launch_date through analysis_end.
    """
    # Filter to launch_date onward
    ad = ad_ic_df[ad_ic_df["day"] >= launch_date]
    ic = ic_df[ic_df["day"] >= launch_date]

    ad_spend = ad["amount_spent"].sum()
    ic_spend = ic["amount_spent"].sum()

    ad_purchases = int(ad["purchases"].sum())
    ic_purchases = int(ic["purchases"].sum())

    ad_revenue = ad["purchase_conversion_value"].sum()
    ad_roas = ad_revenue / ad_spend if ad_spend > 0 else 0.0
    ic_revenue = ic["purchase_conversion_value"].sum()
    ic_roas = ic_revenue / ic_spend if ic_spend > 0 else 0.0

    roas_pct_diff = (ad_roas / ic_roas - 1) * 100 if ic_roas > 0 else 0.0

    # Days running
    last_active = ad["day"].max() if not ad.empty else launch_date
    days_running = (last_active - launch_date).days + 1

    # Days to peak % of IC spend
    peak_info = _days_to_peak_pct(ad, ic, launch_date)

    return {
        "ad_spend": ad_spend,
        "ic_spend": ic_spend,
        "ad_spend_pct_of_ic": ad_spend / ic_spend * 100 if ic_spend > 0 else 0.0,
        "ad_purchases": ad_purchases,
        "ic_purchases": ic_purchases,
        "ad_purchases_pct_of_ic": ad_purchases / ic_purchases * 100 if ic_purchases > 0 else 0.0,
        "ad_roas": ad_roas,
        "ic_roas": ic_roas,
        "roas_pct_diff": roas_pct_diff,
        "days_running": days_running,
        "first_date": launch_date,
        "last_date": last_active,
        "peak_pct_day_num": peak_info["day_num"],
        "peak_pct_date": peak_info["date"],
        "peak_pct_value": peak_info["pct"],
    }


def compute_account_overview(
    ad_all_df: pd.DataFrame,
    ad_ic_df: pd.DataFrame,
    account_df: pd.DataFrame,
    launch_date: date,
    analysis_end: date,
    variations_count: int,
) -> dict:
    """Compute Account Overview metrics (Section 2.1)."""
    # Filter to launch_date onward
    ad = ad_all_df[ad_all_df["day"] >= launch_date]
    acct = account_df[account_df["day"] >= launch_date]

    ad_spend = ad["amount_spent"].sum()
    acct_spend = acct["amount_spent"].sum()

    ad_purchases = int(ad["purchases"].sum())
    acct_purchases = int(acct["purchases"].sum())

    ad_revenue = ad["purchase_conversion_value"].sum()
    ad_roas = ad_revenue / ad_spend if ad_spend > 0 else 0.0
    acct_revenue = acct["purchase_conversion_value"].sum()
    acct_roas = acct_revenue / acct_spend if acct_spend > 0 else 0.0

    roas_pct_diff = (ad_roas / acct_roas - 1) * 100 if acct_roas > 0 else 0.0

    # Days running
    last_active = ad["day"].max() if not ad.empty else launch_date
    days_running = (last_active - launch_date).days + 1

    # Peak spend (first 30 days)
    first_30_end = launch_date + timedelta(days=29)
    ad_first_30 = ad[ad["day"] <= first_30_end]
    peak_30 = _peak_spend_day(ad_first_30, launch_date)

    # Peak spend (all time)
    peak_all = _peak_spend_day(ad, launch_date)

    # Full year reference
    ad_ic_spend_full = ad_ic_df["amount_spent"].sum()
    ad_all_spend_full = ad_all_df["amount_spent"].sum()
    ic_spend_full = None  # computed by caller if needed
    acct_spend_full = account_df["amount_spent"].sum()

    return {
        "ad_spend": ad_spend,
        "acct_spend": acct_spend,
        "ad_spend_pct_of_acct": ad_spend / acct_spend * 100 if acct_spend > 0 else 0.0,
        "ad_purchases": ad_purchases,
        "acct_purchases": acct_purchases,
        "ad_purchases_pct_of_acct": ad_purchases / acct_purchases * 100 if acct_purchases > 0 else 0.0,
        "ad_roas": ad_roas,
        "acct_roas": acct_roas,
        "roas_pct_diff": roas_pct_diff,
        "days_running": days_running,
        "first_date": launch_date,
        "last_date": last_active,
        "peak_30d_day_num": peak_30["day_num"],
        "peak_30d_date": peak_30["date"],
        "peak_30d_spend": peak_30["spend"],
        "peak_all_day_num": peak_all["day_num"],
        "peak_all_date": peak_all["date"],
        "peak_all_spend": peak_all["spend"],
        "variations": variations_count,
        # Full year reference
        "ad_all_spend_full_year": ad_all_spend_full,
        "acct_spend_full_year": acct_spend_full,
        "ad_pct_of_acct_annual": ad_all_spend_full / acct_spend_full * 100 if acct_spend_full > 0 else 0.0,
    }


def compute_ic_full_year_reference(
    ad_ic_df: pd.DataFrame,
    ic_df: pd.DataFrame,
    launch_date: date,
) -> dict:
    """Compute IC Campaign Overview — Full Year Reference (Section 1.11)."""
    ad_spend = ad_ic_df["amount_spent"].sum()
    ic_spend = ic_df["amount_spent"].sum()

    return {
        "launch_date": launch_date,
        "ad_spend_ic": ad_spend,
        "ic_total_spend": ic_spend,
        "ad_pct_of_ic_annual": ad_spend / ic_spend * 100 if ic_spend > 0 else 0.0,
    }


def _days_to_peak_pct(
    ad_df: pd.DataFrame, total_df: pd.DataFrame, launch_date: date
) -> dict:
    """Find the day where ad's daily spend as % of total daily spend was highest."""
    if ad_df.empty:
        return {"day_num": 0, "date": launch_date, "pct": 0.0}

    ad_daily = ad_df.groupby("day")["amount_spent"].sum()
    total_daily = total_df.groupby("day")["amount_spent"].sum()

    # Compute daily percentage
    pct = (ad_daily / total_daily * 100).dropna()
    if pct.empty:
        return {"day_num": 0, "date": launch_date, "pct": 0.0}

    peak_date = pct.idxmax()
    peak_pct = pct.max()
    day_num = (peak_date - launch_date).days

    return {"day_num": day_num, "date": peak_date, "pct": peak_pct}


def _peak_spend_day(ad_df: pd.DataFrame, launch_date: date) -> dict:
    """Find the day with the highest ad spend."""
    if ad_df.empty:
        return {"day_num": 0, "date": launch_date, "spend": 0.0}

    daily = ad_df.groupby("day")["amount_spent"].sum()
    peak_date = daily.idxmax()
    peak_spend = daily.max()
    day_num = (peak_date - launch_date).days

    return {"day_num": day_num, "date": peak_date, "spend": peak_spend}
