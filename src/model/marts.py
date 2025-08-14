import pandas as pd
from ..transform.features import kpi_monthly

# Build thin fact/dim style outputs

def build_fact_orders(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Order ID","Order Date","Ship Date","Customer ID","Segment","Country","City","State","Postal Code","Region",
        "Product ID","Category","Sub-Category","Sales","Quantity","Discount","Profit","Profit Margin","Order Month"
    ]
    return df[cols].copy()

def build_dim_products(df: pd.DataFrame) -> pd.DataFrame:
    return df[['Product ID', 'Product Name', 'Category', 'Sub-Category']].drop_duplicates()

def build_orders_monthly(df: pd.DataFrame) -> pd.DataFrame:
    return kpi_monthly(df)