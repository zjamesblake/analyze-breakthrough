---
name: analyze-breakthrough
description: Run a Breakthrough Analysis for a single ad. Produces a single-tab CSV with IC + Account weekly spend and ROAS data (Weeks 0-8).
---

# /analyze-breakthrough

Generate a breakthrough ad analysis CSV for a single creative.

## Usage

```
/analyze-breakthrough @MyBrand.csv "BATCH#61" --brand "My Brand Name"
```

## Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| CSV file | Yes | Meta Ads Manager CSV export in `account-csvs/` | `@Dog-Friendly-USA.csv` |
| Creative name | Yes | Ad name substring to match (case-insensitive) | `"BATCH#61"` |
| `--brand` | Yes | Brand/account name | `"Dog Friendly USA"` |

If any argument is missing, ask the user for it before proceeding.

## Process

### Step 1: Validate Inputs

- Confirm the CSV file exists in `account-csvs/`
- If the user provides a bare filename, prepend `account-csvs/`
- Confirm they provided a creative name and brand name

### Step 2: Install Dependencies (if needed)

Check if pandas/numpy are available:
```bash
python3 -c "import pandas; import numpy" 2>/dev/null || pip3 install -r requirements.txt
```

### Step 3: Run Analysis

Execute from the `analyze-breakthrough/` directory:
```bash
python3 -c "
from src.breakthrough_export import generate_breakthrough_csv
path = generate_breakthrough_csv(
    csv_path='account-csvs/<CSV_FILE>',
    creative_name='<CREATIVE_NAME>',
    brand_name='<BRAND_NAME>',
)
print(f'Report saved: {path}')
"
```

### Step 4: Verify Output

Read the generated CSV and display a summary:
- Brand, Ad, Account Tier
- Week 1 IC spend % and account spend %
- Confirm it looks reasonable

### Step 5: Troubleshooting

If the script fails with "No rows found matching creative":
- The creative name didn't match any ad names in the CSV
- Note: matching is **case-insensitive** by default
- Ask the user to verify the exact ad name string from their Meta Ads Manager
- They can check by opening the CSV and searching for their ad name
- Common issues: extra spaces, special characters, hash vs underscore

If numbers look wrong (zeros, very small values):
- The ad may have landed in a different campaign than expected
- Ask the user which campaign the ad was originally launched in
- Re-run with `ic_campaign='<campaign name>'` parameter

### Step 6: Report Result

Tell the user:
- The report was saved to `breakthrough-reports/<filename>.csv`
- The detected account tier
- They should verify Week 1-2 numbers against their ad account before submitting
