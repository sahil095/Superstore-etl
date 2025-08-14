import pandas as pd

def to_datetime(df, cols):
    for c in cols:
        df[c] = pd.to_datetime(df[c], errors='coerce')
    return df


def add_order_month(df, col="Order Date", new_col='Order Month'):
    df[new_col] = df[col].dt.to_period('M').dt.to_timestamp()
    return df