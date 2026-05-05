# analyze-breakthrough

> Standalone Claude Code skill that turns a Meta Ads Manager CSV export into a structured breakthrough ad analysis CSV.

## What it does

Takes your full-account Meta Ads Manager export, isolates your winning ad, and produces a standardized CSV with weekly spend %, ROAS %, and week-over-week growth data — ready for the Evolve Winning Ads Study.

## Quick Start

```bash
# 1. Download this folder to your computer
# 2. Open it in Claude Code
cd ~/Desktop/analyze-breakthrough
claude

# 3. Install dependencies (first time only)
pip3 install -r requirements.txt

# 4. Drop your Meta CSV export into account-csvs/

# 5. Run the skill
/analyze-breakthrough @YourExport.csv "YOUR AD NAME" --brand "Your Brand"

# 6. Output appears in breakthrough-reports/
```

## Requirements

- Python 3.8+
- Claude Code
- Meta Ads Manager CSV export (full account, year-to-date, USD, 7-day click attribution)

## Output

Single CSV with metadata header (brand, ad name, auto-detected spend tier) and 4 data sections:
- IC Weekly Spend (Weeks 0-8)
- IC Weekly ROAS (Weeks 0-8)
- Account Weekly Spend (Weeks 0-8)
- Account Weekly ROAS (Weeks 0-8)

## Folder Structure

```
analyze-breakthrough/
├── account-csvs/          ← Drop your Meta CSV exports here
├── breakthrough-reports/  ← Generated reports appear here
├── src/                   ← Processing scripts (do not modify)
├── .claude/skills/        ← Skill definition
├── CLAUDE.md              ← Claude Code instructions
├── CONTEXT.md             ← Project context
├── README.md              ← Full setup guide
└── requirements.txt       ← Python dependencies
```
