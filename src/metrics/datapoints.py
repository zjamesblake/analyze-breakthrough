from typing import List, Optional

from src.constants import CONSECUTIVE_WEEKS_THRESHOLDS, DECAY_THRESHOLDS


def consecutive_weeks_above(
    weekly_pcts: List[Optional[float]], threshold: float
) -> dict:
    """Find longest streak where weekly % >= threshold.

    Args:
        weekly_pcts: List of weekly percentages (index 0 = Week 1).
                     None values are treated as below threshold.
        threshold: Percentage threshold (e.g., 10.0 for 10%).

    Returns dict with: streak_length, start_week, end_week (1-indexed).
    If no streak found, streak_length=0 and start/end=None.
    """
    best_len = 0
    best_start = None
    best_end = None

    current_len = 0
    current_start = None

    for i, pct in enumerate(weekly_pcts):
        week_num = i + 1  # 1-indexed
        if pct is not None and pct >= threshold:
            if current_len == 0:
                current_start = week_num
            current_len += 1
            if current_len > best_len:
                best_len = current_len
                best_start = current_start
                best_end = week_num
        else:
            current_len = 0
            current_start = None

    return {
        "streak_length": best_len,
        "start_week": best_start,
        "end_week": best_end,
    }


def compute_datapoint_a(weekly_pcts: List[Optional[float]]) -> List[dict]:
    """Compute Datapoint A: consecutive weeks above each threshold.

    Args:
        weekly_pcts: List of weekly % of campaign/account (Week 1+, no Week 0).

    Returns list of 3 dicts (one per threshold: 10%, 20%, 30%).
    """
    results = []
    for threshold in CONSECUTIVE_WEEKS_THRESHOLDS:
        threshold_pct = threshold * 100
        streak = consecutive_weeks_above(weekly_pcts, threshold_pct)
        results.append({
            "threshold": threshold_pct,
            **streak,
        })
    return results


def post_peak_decay(weekly_pcts: List[Optional[float]]) -> dict:
    """Analyze post-peak spend share decline.

    Args:
        weekly_pcts: List of weekly % of campaign/account (Week 1+, no Week 0).
                     None values are skipped.

    Returns dict with: peak_week, peak_pct, low_week, low_pct,
    first_below_30, first_below_20, first_below_10
    (week numbers are 1-indexed, None if not found).
    """
    # Find peak
    peak_week = None
    peak_pct = -1.0
    for i, pct in enumerate(weekly_pcts):
        if pct is not None and pct > peak_pct:
            peak_pct = pct
            peak_week = i + 1

    if peak_week is None:
        return {
            "peak_week": None, "peak_pct": 0,
            "low_week": None, "low_pct": 0,
            "first_below_30": None, "first_below_20": None, "first_below_10": None,
        }

    # Find low week and decay thresholds post-peak
    peak_idx = peak_week - 1  # 0-indexed
    low_week = None
    low_pct = float("inf")
    first_below = {t: None for t in DECAY_THRESHOLDS}

    for i in range(peak_idx + 1, len(weekly_pcts)):
        pct = weekly_pcts[i]
        if pct is None:
            continue
        week_num = i + 1

        if pct < low_pct:
            low_pct = pct
            low_week = week_num

        for t in DECAY_THRESHOLDS:
            t_pct = t * 100
            if first_below[t] is None and pct < t_pct:
                first_below[t] = week_num

    if low_week is None:
        low_pct = 0

    return {
        "peak_week": peak_week,
        "peak_pct": peak_pct,
        "low_week": low_week,
        "low_pct": low_pct,
        "first_below_30": first_below[0.30],
        "first_below_20": first_below[0.20],
        "first_below_10": first_below[0.10],
    }


def compute_datapoint_b(weekly_pcts: List[Optional[float]]) -> dict:
    """Compute Datapoint B: post-peak decay analysis.

    Args:
        weekly_pcts: List of weekly % of campaign/account (Week 1+, no Week 0).

    Returns dict with peak info, low info, and first-below thresholds.
    """
    return post_peak_decay(weekly_pcts)
