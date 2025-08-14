from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_CURATED = BASE_DIR / "data" / "curated"
ARTIFACTS = BASE_DIR / "artifacts"
PLOTS_DIR = ARTIFACTS / "plots"


# Raw file location (default)
RAW_CSV = DATA_RAW / "superstore.csv"


# Output files
CLEAN_CSV = DATA_CURATED / "superstore_clean.csv"
ENRICHED_CSV = DATA_CURATED / "superstore_enriched.csv"
MART_ORDERS_MONTHLY = DATA_CURATED / "mart_orders_monthly.csv"
MART_DIM_PROD = DATA_CURATED / "dim_products.csv"
MART_FACT_ORDERS = DATA_CURATED / "fact_orders.csv"

# Create directories on import
for d in (DATA_RAW, DATA_CURATED, PLOTS_DIR):
    d.mkdir(parents=True, exist_ok=True)