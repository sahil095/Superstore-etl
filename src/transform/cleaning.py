import pandas as pd

EXPECTED_COLS = [
    "Order ID","Order Date","Ship Date","Ship Mode","Customer ID","Customer Name",
    "Segment","Country","City","State","Postal Code","Region","Product ID",
    "Category","Sub-Category","Product Name","Sales","Quantity","Discount","Profit"
]

def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    # 1) Trim columns that exists in SuperStore; keep extras if present
    # (We won't drop unknown columns by default; interview-friendly to show flexibility.)


    # 2) Strip whitespace in object columns
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()

    # 3) Fix dtypes
    numeric_cols = ['Sales', 'Quantity', 'Discount', 'Profit']
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    
    # 4) Remove impossible values
    if 'Discount' in df.columns:
        df = df[(df['Discount'] > 0) & (df['Discount'] <= 0.9)]
    

    # 5) Drop duplicates
    df = df.drop_duplicates()

    return df