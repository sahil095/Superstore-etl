# src/viz/dashboard.py

from pathlib import Path
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go

# ====== Global Plotly defaults / Theme ======
px.defaults.template = "plotly_white"
COLORWAY = ["#2F67D8", "#00A38C", "#F39C12", "#8E44AD", "#16A085", "#D35400", "#2C3E50"]

# ====== Data Loading ======
def load_curated(curated_dir: Path):
    fact = pd.read_csv(
        curated_dir / "fact_orders.csv",
        parse_dates=["Order Date", "Ship Date", "Order Month"],
    )
    monthly = pd.read_csv(
        curated_dir / "mart_orders_monthly.csv",
        parse_dates=["Order Month"],
    )
    return fact, monthly

# ====== Helpers ======
def apply_filters(df, start, end, regions, cats, segs):
    if start is None or end is None:
        raise PreventUpdate

    regions = regions or []
    cats = cats or []
    segs = segs or []

    try:
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
    except Exception:
        raise PreventUpdate

    mask = (df["Order Date"] >= start_dt) & (df["Order Date"] <= end_dt)
    if regions:
        mask &= df["Region"].isin(regions)
    if cats:
        mask &= df["Category"].isin(cats)
    if segs:
        mask &= df["Segment"].isin(segs)
    return df.loc[mask].copy()

def no_dim_filters(regions, cats, segs):
    return (not regions) and (not cats) and (not segs)

def empty_fig(title):
    fig = px.scatter(title=title)
    fig.update_layout(
        xaxis={"visible": False}, yaxis={"visible": False},
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

def compute_delta(curr, prev):
    if prev in (None, 0) or (isinstance(prev, float) and (np.isnan(prev) or np.isinf(prev))):
        return None
    try:
        return ((curr - prev) / prev) * 100.0
    except ZeroDivisionError:
        return None

def quick_insights(df_filtered):
    if df_filtered.empty:
        return "No data for the current filter selection."
    cat = df_filtered.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    top_cat = f"{cat.index[0]} (+{cat.iloc[0]:,.0f})" if len(cat) else "—"
    worst_cat = f"{cat.index[-1]} (+{cat.iloc[-1]:,.0f})" if len(cat) > 1 else "—"
    reg = df_filtered.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    top_reg = f"{reg.index[0]} (+{reg.iloc[0]:,.0f})" if len(reg) else "—"
    sales = df_filtered["Sales"].sum()
    profit = df_filtered["Profit"].sum()
    margin = (profit / sales) if sales else 0.0
    return (
        f"Top Category: {top_cat} • Low Category: {worst_cat} • "
        f"Top Region: {top_reg} • Overall Margin: {margin:.1%}"
    )

# ====== App ======
def make_app(curated_dir: Path):
    fact, monthly = load_curated(curated_dir)

    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            # External font (Dash will fetch it)
            html.Link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
            ),

            # Header
            html.Div(
                [
                    html.Div("SuperStore Performance Dashboard", className="title"),
                    html.Div(id="context-subtitle", className="subtitle"),
                ],
                className="header",
            ),

            # Filters
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Date Range", className="label"),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=fact["Order Date"].min(),
                                max_date_allowed=fact["Order Date"].max(),
                                start_date=fact["Order Date"].min(),
                                end_date=fact["Order Date"].max(),
                                display_format="MMM D, YYYY",
                            ),
                        ],
                        className="filter-block",
                    ),
                    html.Div(
                        [
                            html.Div("Quick Range", className="label"),
                            dcc.RadioItems(
                                id="quick-range",
                                options=[
                                    {"label": "7D", "value": "7d"},
                                    {"label": "30D", "value": "30d"},
                                    {"label": "QTD", "value": "qtd"},
                                    {"label": "YTD", "value": "ytd"},
                                    {"label": "ALL", "value": "all"},
                                ],
                                value="all",
                                inline=True,
                                className="radio-inline",
                            ),
                        ],
                        className="filter-block",
                    ),
                    html.Div(
                        [
                            html.Div("Region", className="label"),
                            dcc.Dropdown(
                                id="region-dd",
                                options=[{"label": r, "value": r} for r in sorted(fact["Region"].dropna().unique())],
                                multi=True,
                                placeholder="All",
                            ),
                        ],
                        className="filter-block",
                    ),
                    html.Div(
                        [
                            html.Div("Category", className="label"),
                            dcc.Dropdown(
                                id="category-dd",
                                options=[{"label": c, "value": c} for c in sorted(fact["Category"].dropna().unique())],
                                multi=True,
                                placeholder="All",
                            ),
                        ],
                        className="filter-block",
                    ),
                    html.Div(
                        [
                            html.Div("Segment", className="label"),
                            dcc.Dropdown(
                                id="segment-dd",
                                options=[{"label": s, "value": s} for s in sorted(fact["Segment"].dropna().unique())],
                                multi=True,
                                placeholder="All",
                            ),
                        ],
                        className="filter-block",
                    ),
                ],
                className="filters-row",
            ),

            # KPI row
            html.Div(
                [
                    html.Div([html.Span("💰", className="kpi-icon"), html.Span("Sales", className="kpi-title"),
                              html.Div("$0", id="kpi-sales", className="kpi-value"),
                              html.Div("", className="kpi-delta")], className="kpi-card"),
                    html.Div([html.Span("📈", className="kpi-icon"), html.Span("Profit", className="kpi-title"),
                              html.Div("$0", id="kpi-profit", className="kpi-value"),
                              html.Div("", className="kpi-delta")], className="kpi-card"),
                    html.Div([html.Span("📦", className="kpi-icon"), html.Span("Orders", className="kpi-title"),
                              html.Div("0", id="kpi-orders", className="kpi-value"),
                              html.Div("", className="kpi-delta")], className="kpi-card"),
                    html.Div([html.Span("📊", className="kpi-icon"), html.Span("Margin", className="kpi-title"),
                              html.Div("0.0%", id="kpi-margin", className="kpi-value"),
                              html.Div("", className="kpi-delta")], className="kpi-card"),
                ],
                className="kpi-row",
            ),

            # Charts grid (fixed height → one screen, no scroll)
            html.Div(
                [
                    dcc.Graph(id="ts-sales-profit", config={"displaylogo": False}, className="chart ts",
                                style={"height": "280px", "width": "100%"}),
                    dcc.Graph(id="bar-category", config={"displaylogo": False}, className="chart bar",
                                style={"height": "250px", "width": "100%"}),
                    dcc.Graph(id="heatmap-region-category", config={"displaylogo": False}, className="chart heat",
                                style={"height": "250px", "width": "100%"}),
                    dcc.Graph(id="top-products", config={"displaylogo": False}, className="chart top",
                                style={"height": "520px", "width": "100%"}),
                ],
                className="charts-grid",
            ),

            # Quick Insights panel
            html.Div(id="quick-insights", className="insights"),
        ],
        className="app",
    )

    # ====== Callbacks ======

    # Quick range → update date picker
    @app.callback(
        Output("date-range", "start_date"),
        Output("date-range", "end_date"),
        Input("quick-range", "value"),
        State("date-range", "min_date_allowed"),
        State("date-range", "max_date_allowed"),
    )
    def set_quick_range(preset, min_allowed, max_allowed):
        if preset is None:
            raise PreventUpdate
        min_dt = pd.to_datetime(min_allowed)
        max_dt = pd.to_datetime(max_allowed)
        end = max_dt
        if preset == "7d":
            start = end - pd.Timedelta(days=7)
        elif preset == "30d":
            start = end - pd.Timedelta(days=30)
        elif preset == "qtd":
            q = (end.month - 1) // 3 + 1
            start = pd.Timestamp(end.year, 3 * (q - 1) + 1, 1)
        elif preset == "ytd":
            start = pd.Timestamp(end.year, 1, 1)
        elif preset == "all":
            start = min_dt
        else:
            start = min_dt
        start = max(start, min_dt)
        end = min(end, max_dt)
        return start, end

    @app.callback(
        Output("kpi-sales", "children"),
        Output("kpi-profit", "children"),
        Output("kpi-orders", "children"),
        Output("kpi-margin", "children"),
        Output("ts-sales-profit", "figure", allow_duplicate=True),
        Output("bar-category", "figure"),
        Output("heatmap-region-category", "figure"),
        Output("top-products", "figure"),
        Output("context-subtitle", "children"),
        Output("quick-insights", "children"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("region-dd", "value"),
        Input("category-dd", "value"),
        Input("segment-dd", "value"),
        prevent_initial_call='initial_duplicate'
    )
    def update_all(start, end, regions_v, cats_v, segs_v):
        # 1) Filter
        f = apply_filters(fact, start, end, regions_v, cats_v, segs_v)
        start_dt, end_dt = pd.to_datetime(start), pd.to_datetime(end)

        # Empty state
        if f.empty:
            subtitle = f"{start_dt.date()} → {end_dt.date()} | No data for current filters"
            return (
                "$0", "$0", "0", "0.0%",
                empty_fig("Monthly Sales & Profit"),
                empty_fig("Sales by Category"),
                empty_fig("Sales Heatmap: Region × Category"),
                empty_fig("Top 10 Products by Profit"),
                subtitle,
                "No data for the current filter selection."
            )

        # 2) KPIs
        total_sales  = float(f["Sales"].sum())
        total_profit = float(f["Profit"].sum())
        orders       = int(f["Order ID"].nunique())
        margin       = (total_profit / total_sales) if total_sales else 0.0

        # Deltas (previous equal-length window)
        delta_sales = delta_profit = delta_margin = None
        try:
            window_days = max((end_dt - start_dt).days, 1)
            prev_end = start_dt - pd.Timedelta(days=1)
            prev_start = prev_end - pd.Timedelta(days=window_days)

            if no_dim_filters(regions_v, cats_v, segs_v):
                m_curr = monthly[(monthly["Order Month"] >= start_dt) & (monthly["Order Month"] <= end_dt)]
                m_prev = monthly[(monthly["Order Month"] >= prev_start) & (monthly["Order Month"] <= prev_end)]
                curr_sales = float(m_curr.get("Total_Sales", pd.Series()).sum())
                curr_profit = float(m_curr.get("Total_Profit", pd.Series()).sum())
                prev_sales = float(m_prev.get("Total_Sales", pd.Series()).sum()) or 0.0
                prev_profit = float(m_prev.get("Total_Profit", pd.Series()).sum()) or 0.0
            else:
                m_curr = f
                m_prev = fact[(fact["Order Date"] >= prev_start) & (fact["Order Date"] <= prev_end)]
                curr_sales = float(m_curr["Sales"].sum())
                curr_profit = float(m_curr["Profit"].sum())
                prev_sales = float(m_prev["Sales"].sum()) or 0.0
                prev_profit = float(m_prev["Profit"].sum()) or 0.0

            curr_margin = (curr_profit / curr_sales) if curr_sales else 0.0
            prev_margin = (prev_profit / prev_sales) if prev_sales else 0.0

            delta_sales  = compute_delta(curr_sales, prev_sales)
            delta_profit = compute_delta(curr_profit, prev_profit)
            delta_margin = compute_delta(curr_margin, prev_margin)
        except Exception:
            pass

        k1 = f"${total_sales:,.0f}"
        k2 = f"${total_profit:,.0f}"
        k3 = f"{orders:,d}"
        k4 = f"{margin:.1%}"

        # 3) Time series (Area). Use monthly mart if no dim filters
        if no_dim_filters(regions_v, cats_v, segs_v):
            ts = monthly[(monthly["Order Month"] >= start_dt) & (monthly["Order Month"] <= end_dt)].sort_values("Order Month")
            fig_ts = go.Figure()
            if {"Total_Sales", "Total_Profit"}.issubset(ts.columns):
                fig_ts.add_trace(go.Scatter(x=ts["Order Month"], y=ts["Total_Sales"], mode="lines", name="Sales", fill="tozeroy"))
                fig_ts.add_trace(go.Scatter(x=ts["Order Month"], y=ts["Total_Profit"], mode="lines", name="Profit", fill="tozeroy"))
                fig_ts.update_layout(title="Monthly Sales & Profit (pre-aggregated)",
                                     margin=dict(l=10,r=10,t=40,b=10),
                                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                     colorway=COLORWAY)
            else:
                fig_ts = px.area(ts, x="Order Month", y=[c for c in ts.columns if "Total" in c], title="Monthly Sales & Profit")
        else:
            ts = (f.groupby("Order Month").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index().sort_values("Order Month"))
            fig_ts = px.area(ts, x="Order Month", y=["Sales","Profit"], title="Monthly Sales & Profit (filtered)")
            fig_ts.update_layout(margin=dict(l=10,r=10,t=40,b=10),
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                 colorway=COLORWAY)

        # Peak annotation
        try:
            col = "Sales" if "Sales" in ts.columns else "Total_Sales"
            peak_idx = ts[col].idxmax()
            fig_ts.add_annotation(x=ts.loc[peak_idx, "Order Month"], y=ts.loc[peak_idx, col],
                                  text=f"Peak: {ts.loc[peak_idx, col]:,.0f}",
                                  showarrow=True, arrowhead=1, yshift=18)
        except Exception:
            pass

        # 4) Category bars (horizontal, labeled)
        cat = f.groupby("Category").agg(Sales=("Sales","sum")).reset_index().sort_values("Sales", ascending=True)
        fig_bar = px.bar(cat, x="Sales", y="Category", orientation="h",
                         title="Sales by Category", text="Sales", color="Category")
        fig_bar.update_layout(margin=dict(l=10,r=10,t=40,b=10), showlegend=False, colorway=COLORWAY)
        fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)

        # 5) Region × Category heatmap (with labels)
        heat = (f.pivot_table(values="Sales", index="Region", columns="Category", aggfunc="sum", fill_value=0)
                  .reset_index().melt(id_vars="Region", var_name="Category", value_name="Sales"))
        fig_heat = px.density_heatmap(heat, x="Category", y="Region", z="Sales",
                                      color_continuous_scale="Blues",
                                      title="Sales Heatmap: Region × Category")
        fig_heat.update_traces(hovertemplate="Region=%{y}<br>Category=%{x}<br>Sales=%{z:,.0f}<extra></extra>", showscale=True)
        fig_heat.update_layout(margin=dict(l=10,r=10,t=40,b=10))

        # 6) Top products (horizontal bar)
        top = (f.groupby("Product Name").agg(Profit=("Profit","sum")).reset_index()
                 .sort_values("Profit", ascending=True).tail(10))
        fig_top = px.bar(top, x="Profit", y="Product Name", orientation="h",
                         title="Top 10 Products by Profit", text="Profit", color="Profit")
        fig_top.update_layout(margin=dict(l=10,r=10,t=40,b=10), coloraxis_showscale=False, showlegend=False)
        fig_top.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)

        # 7) Subtitle & Quick Insights
        active = []
        if regions_v: active.append(f"Regions: {', '.join(regions_v)}")
        if cats_v:    active.append(f"Categories: {', '.join(cats_v)}")
        if segs_v:    active.append(f"Segments: {', '.join(segs_v)}")
        filters_txt = " | ".join(active) if active else "All Regions • All Categories • All Segments"
        subtitle = f"{pd.to_datetime(start).date()} → {pd.to_datetime(end).date()}  |  {filters_txt}"
        insights = quick_insights(f)

        return k1, k2, k3, k4, fig_ts, fig_bar, fig_heat, fig_top, subtitle, insights
    
    @app.callback(
        Output("ts-sales-profit", "figure", allow_duplicate=True),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("quick-range", "value"),   # <-- dropdown or radio for 7D/30D
        prevent_initial_call='initial_duplicate',
    )
    def update_timeseries(start_date, end_date, quick_range):
        df = monthly.copy()
        print(df.head())
        # --- Quick range override ---
        if quick_range == "7D":
            end_date = df["Order Date"].max()
            start_date = end_date - pd.Timedelta(days=7)
        elif quick_range == "30D":
            end_date = df["Order Date"].max()
            start_date = end_date - pd.Timedelta(days=30)

        # --- Filter data ---
        mask = (df["Order Date"] >= pd.to_datetime(start_date)) & \
            (df["Order Date"] <= pd.to_datetime(end_date))
        filtered = df.loc[mask]

        fig = px.line(
            filtered,
            x="Order Date",
            y=["Sales", "Profit"],
            title="Sales & Profit Over Time"
        )
        fig.update_layout(margin=dict(l=40, r=20, t=40, b=40))
        return fig

    return app

if __name__ == "__main__":
    from src.config import DATA_CURATED
    app = make_app(DATA_CURATED)
    app.run_server(debug=True)
