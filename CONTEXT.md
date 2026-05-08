# Breakthrough Analyzer — Context

**Owner:** Ecom Talent / Evolve Program
**Purpose:** Enable Evolve members to self-serve breakthrough ad analysis and submit standardized data for the Winning Ads Study.
**Tech:** Python, pandas, Claude Code skill
**Status:** Active

---

## What This Is

A shareable, standalone Claude Code skill package. Evolve members download this folder, install dependencies, and use the `/analyze-breakthrough` skill to process their Meta Ads Manager exports into structured CSVs.

The output CSVs are submitted to Spencer/Jed for inclusion in the master Winning Ads Analysis — a growing dataset that defines breakthrough ad benchmarks by spend tier.

## How It Fits Into the Bigger Picture

```
Member exports CSV → runs /analyze-breakthrough → verifies numbers → submits CSV
                                                                         ↓
                                                Spencer/Jed paste into master sheet
                                                                         ↓
                                                Master auto-calculates medians/min/max
                                                                         ↓
                                                Winning Ads Analysis doc gets updated
```

## Key Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| One ad per run | Yes | Avoids confusion; run again for additional ads |
| Case-insensitive matching | Default | Members won't know about Meta's casing inconsistencies |
| Auto-detect IC | Yes | Most members won't know which campaign launched first |
| Auto-calculate tier | Yes | Removes manual input error |
| Single-tab stacked CSV | Yes | Spencer's master sheet ingests one tab per ad |
| Weeks 0-8 only | Yes | Consistent window across all submissions |

## Dependencies

- `pandas` and `numpy` (installed via `pip3 install -r requirements.txt`)
- Python 3.8+
- Claude Code (for the `/analyze-breakthrough` skill)

## Output Format

Single CSV with metadata header + 4 stacked sections:
1. **IC Weekly Spend** — `Week, Ad % of Campaign, Ad $, IC $, IC Spend WoW Δ%`
2. **IC Weekly ROAS** — `Week, Ad % vs Campaign, Ad ROAS (#), IC ROAS (#)`
3. **Account Weekly Spend** — `Week, Ad % of Account, Ad $, Account $, Account Spend WoW Δ%`
4. **Account Weekly ROAS** — `Week, Ad % vs Account, Ad ROAS (#), Account ROAS (#)`

The ROAS `(#)` columns are absolute values computed from raw revenue/spend for that weekly period — not derived from the `Ad % vs` column.

Sections separated by `--- LABEL ---` rows for human readability and programmatic parsing.
