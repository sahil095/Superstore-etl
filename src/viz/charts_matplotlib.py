import matplotlib.pyplot as plt
from pathlib import Path

# Simple reusable Matplotlib charts (static exports)

def bar_sales_by_category(df, save_path: Path):
    s = df.groupby('Category')['Sales'].sum()
    plt.figure(figsize=(8,5))
    s.plot(kind='bar')
    plt.title('Total Sales by Category')
    plt.xlabel('Category'); plt.ylabel('Sales ($)')
    for i, v in enumerate(s.values):
        plt.text(i, v, f"{v:,.0f}", ha='center', va='bottom')
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight'); plt.close()