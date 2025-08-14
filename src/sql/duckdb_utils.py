import duckdb
import pandas as pd
from pathlib import Path

# Open an in-memory DB (or pass a file path to persist)

def query_csvs(curated_dir: Path, sql: str) -> pd.DataFrame:
    con = duckdb.connect()
    # Auto-scan curated CSVs
    con.execute(f"CREATE VIEW fact_orders AS SELECT * FROM read_csv_auto('{(curated_dir/'fact_orders.csv').as_posix()}')")
    con.execute(f"CREATE VIEW dim_products AS SELECT * FROM read_csv_auto('{(curated_dir/'dim_products.csv').as_posix()}')")
    con.execute(f"CREATE VIEW mart_orders_monthly AS SELECT * FROM read_csv_auto('{(curated_dir/'mart_orders_monthly.csv').as_posix()}')")
    return con.execute(sql).df()