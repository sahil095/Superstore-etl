import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def iqr_flags(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    # compute Q1/Q3/IQR per group and join back
    stats = df.groupby(group_col)[value_col].quantile([0.25, 0.75]).unstack()
    stats.columns = ['Q1', 'Q3']
    stats['IQR'] = stats['Q3'] - stats['Q1']
    outlier = df.join(stats, on = group_col)
    outlier['is_outlier'] = (outlier[value_col] < (outlier['Q1'] - 1.5*outlier['IQR'])) | \
                            (outlier[value_col] > (outlier['Q3'] + 1.5*outlier['IQR']))
    return outlier


def plot_outlier_box(df_flagged: pd.DataFrame, group_val: str, group_col: str, value_col: str, save_path: Path):
    sub = df_flagged[df_flagged[group_col] == group_val]
    plt.figure(figsize=(8, 4))
    plt.boxplot(sub[value_col].dropna(), vert=True)
    plt.title(f"{group_val}: {value_col} with IQR Outliers")
    plt.ylabel(value_col)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()


def plot_outliers_scatter(df_flagged: pd.DataFrame, value_x: str, value_y: str, flag_col: str, save_path: Path):
    plt.figure(figsize=(8,5))
    normal = df_flagged[~df_flagged[flag_col]]
    outl = df_flagged[df_flagged[flag_col]]
    plt.scatter(normal[value_x], normal[value_y], s=10, alpha=0.5, label='Normal')
    plt.scatter(outl[value_x], outl[value_y], s=20, alpha=0.8, label='Outlier', marker='x')
    plt.xlabel(value_x); plt.ylabel(value_y)
    plt.title(f"Outlier Highlight: {value_y} vs {value_x}")
    plt.legend()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()