import pandas as pd

# Reusable aggregations for marts and dashboard

def kpi_monthly(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("Order Month").agg(
        Total_Sales = ('Sales', 'sum'),
        Total_Profit = ('Profit', 'sum'),
        Orders = ('Order ID', 'nunique'),
        Customers = ('Customer ID', 'nunique'),
        Avg_Discount = ('Discount', 'mean'),
        Profit_Margin = ("Profit", lambda x: x.sum()/df.loc[x.index, "Sales"].sum() if df.loc[x.index, "Sales"].sum() else 0)
    ).reset_index()
    return g


def by_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(['Category']).agg(
        Sales=('Sales', 'sum'), Profit=('Profit', 'sum'), Quantity=('Quantity', 'sum')
    ).reset_index()


def by_region_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot_table(values='Sales', index='Region', columns='Category', aggfunc='sum').reset_index()


def top_products(df: pd.DataFrame, n = 10) -> pd.DataFrame:
    s = df.groupby('Product Name').agg(Sales = ('Sales', 'sum'), Profit=('Proft', 'sum')).reset_index()
    return s.sort_values('Profit', ascending=False).head(n)