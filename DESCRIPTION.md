# analyze-breakthrough

> Turn your Meta Ads data into a breakthrough ad report — in one command.

## Quick Start

1. Download this folder (green **Code** button → **Download ZIP**)
2. Place `analyze-breakthrough/` in your Claude Code workspace
3. Open Claude Code and say: "Go into analyze-breakthrough and install the requirements"
4. Drop your Meta Ads Manager CSV into `account-csvs/`
5. Run: `/analyze-breakthrough @YourFile.csv "AD NAME" --brand "Brand Name"`
6. Your report appears in `breakthrough-reports/`

## Requirements

- Claude Code (https://claude.ai/code)
- A Meta Ads Manager CSV export (full account, year-to-date, USD, 7-day click)

## What it does

Takes your full-account Meta export, isolates your winning ad, and produces a CSV with:
- Weekly spend % and ROAS % (Weeks 0-8)
- Week-over-week growth
- Auto-detected spend tier and initial campaign

One ad per report. Run it again for additional ads.

## Folder Structure

```
analyze-breakthrough/
├── account-csvs/          ← Drop your CSV exports here
├── breakthrough-reports/  ← Reports appear here
├── src/                   ← Processing scripts (don't touch)
├── README.md              ← Full instructions
└── requirements.txt       ← Python dependencies (installed once)
```
