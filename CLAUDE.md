# Breakthrough Analyzer

Standalone tool that processes a Meta Ads Manager CSV export and generates a breakthrough ad analysis CSV for a single creative.

## Quick Start

1. Place your Meta Ads Manager CSV export in `account-csvs/`
2. Run `/analyze-breakthrough @YourFile.csv "YOUR_AD_NAME" --brand "Your Brand"`
3. Output lands in `breakthrough-reports/`

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `account-csvs/` | Drop your Meta CSV exports here |
| `breakthrough-reports/` | Generated reports appear here |
| `src/` | Python processing scripts (do not modify) |

## Requirements

- Python 3.8+
- pandas, numpy (`pip3 install -r requirements.txt`)
- Claude Code

## CSV Export Instructions

When exporting from Meta Ads Manager:

1. **Date range:** Year-to-date (January 1 through today)
2. **Currency:** USD (critical — non-USD will produce incorrect results)
3. **Attribution:** 7-day click
4. **Columns required:** Ad name, Campaign name, Day, Amount spent, Purchases, Cost per purchase, Purchases conversion value, ROAS, Reporting starts, Reporting ends
5. **Level:** Ad level (not campaign or account)
6. **Scope:** Entire account (all campaigns, all ads)

## Notes

- Creative matching is **case-insensitive** — "batch#61" matches "BATCH#61"
- The IC (Initial Campaign) is auto-detected as the first campaign the ad appeared in
- Account spend tier is auto-calculated from the CSV data
- Output covers Weeks 0-8 only (first 9 weeks from ad launch)
