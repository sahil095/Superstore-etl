import argparse
import pandas as pd
from src.config import RAW_CSV, CLEAN_CSV, ENRICHED_CSV, DATA_CURATED, PLOTS_DIR, MART_FACT_ORDERS, MART_DIM_PROD, MART_ORDERS_MONTHLY
from src.ingest.readers import read_local_csv
from src.transform.cleaning import basic_clean
from src.transform.enrich import add_enriched_fields
from src.transform.outliers import iqr_flags, plot_outlier_box, plot_outliers_scatter
from src.model.marts import build_fact_orders, build_dim_products, build_orders_monthly
from src.utils.io import to_csv



def run_etl(raw_path = RAW_CSV):
    print("[INGEST] Reading raw CSV…", raw_path)
    df = read_local_csv(raw_path)

    print("[CLEAN] Basic cleaning…")
    df = basic_clean(df)
    to_csv(df, CLEAN_CSV)

    print("[ENRICH] Derived fields…")
    df = add_enriched_fields(df)
    to_csv(df, ENRICHED_CSV)

    print("[MARTS] Building curated tables…")
    fact = build_fact_orders(df); to_csv(fact, MART_FACT_ORDERS)
    dimp = build_dim_products(df); to_csv(dimp, MART_DIM_PROD)
    monthly = build_orders_monthly(df); to_csv(monthly, MART_ORDERS_MONTHLY)

    print("[OUTLIERS] Flag + visuals (Profit by Sub-Category)…")
    flagged = iqr_flags(df, group_col='Sub-Category', value_col='Profit')
    # Save a few images (example):
    plot_outlier_box(flagged, group_val='Binders', group_col='Sub-Category', value_col='Profit', save_path=PLOTS_DIR/"binders_profit_box.png")
    plot_outliers_scatter(flagged, value_x='Sales', value_y='Profit', flag_col='is_outlier', save_path=PLOTS_DIR/"scatter_profit_outliers.png")

    print("[DONE] ETL complete. Curated CSVs & plots ready.")


def run_dashboard():
    from src.viz.dashboard import make_app
    from src.config import DATA_CURATED
    app = make_app(DATA_CURATED)
    app.run(debug=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SuperStore ETL & Dashboard")
    parser.add_argument('--run', choices=['etl','dash'], default='etl')
    parser.add_argument('--raw', help='Path to raw CSV (optional)')
    args = parser.parse_args()

    if args.run == 'etl':
        run_etl(args.raw or RAW_CSV)
    elif args.run == 'dash':
        run_dashboard()