import pandas as pd
from ..utils.dates import to_datetime, add_order_month

def add_enriched_features(df: pd.DataFrame) -> pd.DataFrame:
    # parse dates
    df = to_datetime(df, ['Order Date', 'Ship Date'])

    # derived metrics
    df['Profit Margin'] = df.apply(
        lambda r: (r['Profit']/r['Sales']) if r['Sales'] else 0, axis=1
    )
    df = add_order_month(df, col='Order Date', new_col='Order Month')
    return df