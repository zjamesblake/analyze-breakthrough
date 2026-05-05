# Account threshold tiers (monthly avg spend)
# Each tuple: (lower_bound, upper_bound, label)
ACCOUNT_TIERS = [
    (0, 50_000, "$0-$50K/month"),
    (50_000, 100_000, "$50K-100K/month"),
    (100_000, 250_000, "$100K-250K/month"),
    (250_000, 500_000, "$250K-500K/month"),
    (500_000, 1_000_000, "$500K-1M/month"),
    (1_000_000, float("inf"), "Over $1M/month"),
]

# Consecutive weeks thresholds (Datapoints A)
CONSECUTIVE_WEEKS_THRESHOLDS = [0.10, 0.20, 0.30]

# Post-peak decay thresholds (Datapoints B)
DECAY_THRESHOLDS = [0.30, 0.20, 0.10]

# ROAS neutral band: within +/-2% of benchmark counts as "neutral"
NEUTRAL_ROAS_THRESHOLD = 0.02

# High performer threshold: ad accounting for >10% of spend
HIGH_PERFORMER_THRESHOLD = 0.10

# Scaling analysis window (weeks)
SCALING_WINDOW_WEEKS = 8

# Checkpoint days from launch
CHECKPOINT_DAYS = [0, 3, 7, 14, 30]

# Static "Important Context" paragraph for scaling analysis sections
IMPORTANT_CONTEXT_TEMPLATE = (
    "**Important Context:** When evaluating horizontal scaling (running the same ad across "
    "multiple campaigns), it's expected to see some ROAS decline as spend increases. This is "
    "a normal market response — as you reach more of the audience, the marginal ROAS decreases. "
    "The key metric is whether the ad maintains a profitable ROAS at higher spend levels, not "
    "whether ROAS stays flat."
)

# Column rename map: Meta Ads CSV header -> canonical name
COLUMN_RENAME_MAP = {
    "Campaign name": "campaign_name",
    "Ad name": "ad_name",
    "Day": "day",
    "Currency": "currency",
    "Amount spent (USD)": "amount_spent",
    "Amount spent (CAD)": "amount_spent",
    "Attribution setting": "attribution_setting",
    "Purchases": "purchases",
    "Cost per purchase": "cost_per_purchase",
    "Purchases conversion value": "purchase_conversion_value",
    "ROAS (all)": "roas",
    "Reporting starts": "reporting_starts",
    "Reporting ends": "reporting_ends",
}
