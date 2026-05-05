# Breakthrough Analyzer

Generate breakthrough ad analysis reports from your Meta Ads Manager data.

This tool processes a full-account CSV export, isolates a specific winning ad, and produces a standardized CSV with weekly spend and ROAS performance data — ready to submit for the Evolve Winning Ads Study.

---

## Setup (One-Time)

### 1. Download this folder

Place the `analyze-breakthrough/` folder anywhere on your computer (Desktop works fine).

### 2. Install Claude Code

If you don't already have it: https://claude.ai/code

### 3. Open in Claude Code

```bash
cd ~/Desktop/analyze-breakthrough
claude
```

### 4. Install Python dependencies

When Claude Code opens, run:
```
pip3 install -r requirements.txt
```

That's it. You're ready to run reports.

---

## Usage

### 1. Export your CSV from Meta Ads Manager

- **Date range:** January 1 through today (year-to-date)
- **Level:** Ad
- **Currency:** USD (important!)
- **Attribution:** 7-day click
- **Scope:** All campaigns in the account
- **Columns:** Ad name, Campaign name, Day, Amount spent, Purchases, Cost per purchase, Purchases conversion value, ROAS, Reporting starts, Reporting ends

Save the exported CSV into the `account-csvs/` folder inside this directory.

### 2. Run the analysis

In Claude Code, type:
```
/analyze-breakthrough @YourExport.csv "YOUR AD NAME" --brand "Your Brand"
```

Replace:
- `YourExport.csv` with your CSV filename
- `YOUR AD NAME` with the name (or part of the name) of your winning ad
- `Your Brand` with your brand name

### 3. Verify the output

The report will be saved to `breakthrough-reports/`. Open it and spot-check Week 1-2 numbers against your ad account to confirm accuracy.

### 4. Submit

Send the generated CSV to Spencer for inclusion in the Winning Ads Study.

---

## Troubleshooting

**"No rows found matching creative"**
- Your ad name didn't match anything in the CSV
- Open your CSV in a spreadsheet and search for your ad to find the exact name
- Try a shorter substring (e.g., "BATCH#61" instead of the full ad name)

**Numbers look wrong (all zeros or very small)**
- The tool auto-detects which campaign launched your ad first
- If it picked the wrong campaign, tell Claude Code which campaign to use:
  - "Re-run but use campaign 'My Campaign Name' as the IC"

**"ModuleNotFoundError: No module named 'pandas'"**
- Run `pip3 install -r requirements.txt` first

---

## What the output contains

A single CSV with your brand info at the top, then 4 data sections:

1. **IC Weekly Spend** — How much of the initial campaign your ad captured (Weeks 0-8)
2. **IC Weekly ROAS** — Your ad's ROAS vs the campaign average
3. **Account Weekly Spend** — How much of total account spend your ad captured
4. **Account Weekly ROAS** — Your ad's ROAS vs account average

Each section includes week-over-week growth percentages so you can see how fast the campaign/account scaled after your ad launched.
