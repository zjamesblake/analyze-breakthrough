# Breakthrough Analyzer

Turn your Meta Ads data into a breakthrough ad report — in one command.

---

## Setup

### Step 1: Download this folder

Click the green **Code** button above, then **Download ZIP**. Unzip it.

### Step 2: Place it in your Claude Code workspace

Move the `analyze-breakthrough` folder into whatever folder you use with Claude Code. If you don't have one yet, your Desktop is fine.

### Step 3: Open Claude Code and install

Open Claude Code in the folder where you placed `analyze-breakthrough`. Then tell Claude:

> "Go into the analyze-breakthrough folder and install the requirements"

Claude will run `pip3 install -r requirements.txt` for you. This only needs to happen once.

---

## How to Run a Report

### Step 1: Export your data from Meta Ads Manager

Spencer will walk you through this in the Loom video. The key points:

- Export at the **Ad level**
- **Full account** (all campaigns)
- **Year-to-date** date range
- **USD** currency
- **7-day click** attribution

Save the file into the `analyze-breakthrough/account-csvs/` folder.

### Step 2: Run the command

In Claude Code, type:

```
/analyze-breakthrough @YourFile.csv "YOUR AD NAME" --brand "Your Brand"
```

Replace:
- `YourFile.csv` — your export filename
- `YOUR AD NAME` — the name of your winning ad (or part of it)
- `Your Brand` — your brand name

### Step 3: Check your numbers

Claude will show you a summary. Compare Week 1 and Week 2 numbers against your ad account to make sure they match.

### Step 4: Submit

Send the generated file (in `breakthrough-reports/`) to Spencer.

---

## Troubleshooting

**"No rows found matching creative"**

Your ad name didn't match. Open your CSV in Google Sheets and search for your ad to see the exact name. You only need a piece of it — for example, "BATCH#61" instead of the full name.

**Numbers look wrong**

Tell Claude: "The numbers look off — can you try using [campaign name] as the initial campaign?" (Use the campaign your ad was originally launched in.)

**"No module named pandas"**

Tell Claude: "Please install the requirements." It will run the install for you.

---

## What you get

A CSV file with your brand info and 4 sections of weekly data (Weeks 0-8):

1. **IC Weekly Spend** — What % of the campaign your ad captured
2. **IC Weekly ROAS** — Your ad's ROAS vs campaign average
3. **Account Weekly Spend** — What % of total account spend your ad captured
4. **Account Weekly ROAS** — Your ad's ROAS vs account average

The tool automatically detects your account's spend tier and which campaign your ad launched in.
