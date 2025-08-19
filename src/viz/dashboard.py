import numpy as np
import pandas as pd
import datetime as dt
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from dash import Dash, dcc, html, Input, Output, State

# ---------- Theming ----------
# Global Plotly defaults
px.defaults.template = "plotly_white"
COLORWAY = ["#2F67D8", "#00A38C", "#F39C12", "#8E44AD", "#16A085", "#D35400", "#2C3E50"]


# ---------- Data Loading ----------
# Load curated CSVs for the app (lightweight for demo)
def load_curated(curated_dir: Path):
    fact = pd.read_csv(curated_dir / 'fact_orders.csv', parse_dates=['Order Date','Ship Date','Order Month'])
    monthly = pd.read_csv(curated_dir / 'mart_orders_monthly.csv', parse_dates=['Order Month'])
    return fact, monthly


# ---------- Helpers ----------
def apply_filters(df, start, end, regions, cats, segs):
        if start is None or end is None:
            # Inputs not ready yet
            raise PreventUpdate

        # Normalize list inputs
        regions = regions or []
        cats = cats or []
        segs = segs or []

        try:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
        except Exception:
            # Bad date values, skip update
            raise PreventUpdate

        m = (df['Order Date'] >= start_dt) & (df['Order Date'] <= end_dt)
        if regions:
            m &= df['Region'].isin(regions)
        if cats:
            m &= df['Category'].isin(cats)
        if segs:
            m &= df['Segment'].isin(segs)

        filtered = df.loc[m].copy()
        return filtered


def _no_dim_filters(regions, cats, segs):
    return (not regions) and (not cats) and (not segs)


def empty_fig(title):
    fig = px.scatter(title=title)
    fig.update_layout(
        xaxis={"visible": False}, yaxis={"visible": False}, margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig


def kpi_card(title, value, delta=None, delta_positive=True, _id=None):
    delta_txt = ""
    delta_color = "#00A38C" if delta_positive else "#D35400"
    if delta is not None:
        sign = "+" if delta >= 0 else ""
        delta_txt = f"{sign}{delta:.1f}%"

    return html.Div(
        [
            html.Div(title, className="kpi-title"),
            html.Div(value, className="kpi-value", id=_id),
            html.Div(delta_txt, className="kpi-delta", style={"color": delta_color}),
        ],
        className="kpi-card",
    )


def compute_period_delta(curr, prev):
    if prev == 0 or prev is None or np.isnan(prev):
        return None
    return ((curr - prev) / prev) * 100.0


# # ---------- App ----------
# def make_app(curated_dir: Path):
#     fact, monthly = load_curated(curated_dir)

#     app = Dash(__name__, suppress_callback_exceptions=True)

#     regions = sorted(fact['Region'].dropna().unique())
#     categories = sorted(fact['Category'].dropna().unique())
#     segments = sorted(fact['Segment'].dropna().unique())

#     # ---------- CSS (inline for single-file portability) ----------
#     app.layout = html.Div([
#         html.H2("Superstore Performance Dashboard"),
#         html.P("Dynamic filters: time range, region, category, segment"),

#         html.Div([
#             dcc.DatePickerRange(
#                 id = 'date-range',
#                 start_date=fact['Order Date'].min(),
#                 end_date=fact['Order Date'].max()
#             ),
#             dcc.Dropdown(options=[{'label': r, 'value': r} for r in regions], id = 'region-dd', multi=True, placeholder='Region'),
#             dcc.Dropdown(options=[{'label': c, 'value': c} for c in categories], id='category-dd', multi=True, placeholder='Category'),
#             dcc.Dropdown(options=[{'label': s, 'value': s} for s in segments], id='segment-dd', multi=True, placeholder='Segment')
#         ], style={'display':'grid', 'gridTemplateColumns':'1fr 1fr 1fr 1fr','gap':'10px'}),
        
#         html.Hr(),

#         # KPI cards (simple)
#         html.Div([
#             html.Div(id='kpi-sales', className='kpi'),
#             html.Div(id='kpi-profit', className='kpi'),
#             html.Div(id='kpi-orders', className='kpi'),
#             html.Div(id='kpi-margin', className='kpi'),
#         ], style={'display':'grid','gridTemplateColumns':'repeat(4, 1fr)','gap':'10px'}),

#         html.Hr(),

#         # Time Series
#         dcc.Graph(id = 'ts-sales-profit'),

#         # Contribution bars
#         dcc.Graph(id = 'bar-category'),

#         # Heatmap: Region x Category by Sales
#         dcc.Graph(id = 'heatmap-region-category'),

#         # Top products table (as bar)
#         dcc.Graph(id = 'top-products')
#     ], style={'padding': '12px'})
    

    
#     @app.callback(
#         Output('kpi-sales','children'), 
#         Output('kpi-profit','children'), 
#         Output('kpi-orders','children'), 
#         Output('kpi-margin','children'),
#         Output('ts-sales-profit','figure'), 
#         Output('bar-category','figure'), 
#         Output('heatmap-region-category','figure'), 
#         Output('top-products','figure'),
#         Input('date-range','start_date'), 
#         Input('date-range','end_date'),
#         Input('region-dd','value'), 
#         Input('category-dd','value'), 
#         Input('segment-dd','value')
#     )
#     def update_all(start, end, regions_v, cats_v, segs_v):
#         f = apply_filters(fact, start, end, regions_v, cats_v, segs_v)

#         total_sales = f['Sales'].sum()
#         total_profit = f['Profit'].sum()
#         orders = f['Order ID'].nunique()
#         margin = (total_profit/total_sales) if total_sales else 0
#         k1 = html.H4(f"Sales: ${total_sales:,.0f}")
#         k2 = html.H4(f"Profit: ${total_profit:,.0f}")
#         k3 = html.H4(f"Orders: ${orders:,.0f}")
#         k4 = html.H4(f"Margin: ${margin:.1%}")
#         if f.empty:
#             k1 = html.H4("Sales: $0")
#             k2 = html.H4("Profit: $0")
#             k3 = html.H4("Orders: 0")
#             k4 = html.H4("Margin: 0.0%")
#             empty_ts = px.line(title='Monthly Sales & Profit (no data)')
#             empty_bar = px.bar(title='Sales by Category (no data)')
#             empty_heat = px.density_heatmap(title='Sales Heatmap: Region x Category (no data)')
#             empty_top = px.bar(title='Top 10 Products by Profit (no data)')
#             return k1, k2, k3, k4, empty_ts, empty_bar, empty_heat, empty_top

#         # # Time Series
#         # ts = f.groupby('Order Month').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
#         # fig_ts = px.line(ts, x='Order Month', y=['Sales','Profit'], title='Monthly Sales & Profit')

#         # --- Time series ---
#         if _no_dim_filters(regions_v, cats_v, segs_v):
#             # Use pre-aggregated monthly mart (fast path)
#             ts = monthly[
#                 (monthly['Order Month'] >= pd.to_datetime(start)) &
#                 (monthly['Order Month'] <= pd.to_datetime(end))
#             ].sort_values('Order Month')

#             # The mart has Total_Sales / Total_Profit columns
#             fig_ts = px.line(
#                 ts,
#                 x='Order Month',
#                 y=['Total_Sales','Total_Profit'],
#                 title='Monthly Sales & Profit (pre-aggregated)'
#             )
#             fig_ts.update_traces(mode='lines+markers')
#         else:
#             # Fall back to on-the-fly aggregation when filters are applied
#             ts = (
#                 f.groupby('Order Month')
#                 .agg(Sales=('Sales','sum'), Profit=('Profit','sum'))
#                 .reset_index()
#                 .sort_values('Order Month')
#             )
#             fig_ts = px.line(
#                 ts,
#                 x='Order Month',
#                 y=['Sales','Profit'],
#                 title='Monthly Sales & Profit (filtered)'
#             )
#             fig_ts.update_traces(mode='lines+markers')

        
#         # Category contribution
#         cat = f.groupby('Category').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
#         fig_bar = px.bar(cat, x='Category', y='Sales', color='Category', title='Sales by Category', text='Sales')

#         # Heatmap Region x Category
#         heat = f.pivot_table(values='Sales', index='Region', columns='Category', aggfunc='sum', fill_value=0)
#         heat = heat.reset_index().melt(id_vars='Region', var_name='Category', value_name='Sales')
#         fig_heat = px.density_heatmap(heat, x='Category', y='Region', z='Sales', color_continuous_scale='Blues', title='Sales Heatmap: Region x Category')

#         # Top products
#         top = f.groupby('Product Name').agg(Profit=('Profit','sum')).reset_index().sort_values('Profit', ascending=False).head(10)
#         fig_top = px.bar(top.sort_values('Profit', ascending=True), x='Profit', y='Product Name', orientation = 'h', title='Top 10 Products by Profit')

#         return k1, k2, k3, k4, fig_ts, fig_bar, fig_heat, fig_top
    
#     return app



# ---------- App ----------
def make_app(curated_dir: Path):
    fact, monthly = load_curated(curated_dir)

    app = Dash(__name__, suppress_callback_exceptions=True)

    # Theme tokens to reuse colors
    THEME = {
        "bg": "#f7f8fb",
        "card": "#ffffff",
        "muted": "#6b7280",
        "text": "#111827",
        "accent": "#2F67D8",
    }

    # ---------- CSS (inline for single-file portability) ----------
    app.layout = html.Div(
        [
            # Google Fonts
            html.Link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
            ),

            # Header
            html.Div(
                [
                    html.Div(
                        "SuperStore Performance Dashboard",
                        className="title",
                        style={"fontWeight": 700, "fontSize": "22px", "color": THEME["text"]},
                    ),
                    html.Div(
                        id="context-subtitle",
                        className="subtitle",
                        style={"color": THEME["muted"], "fontSize": "13px"},
                    ),
                ],
                className="header",
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "baseline",
                    "padding": "10px 14px",
                    "background": THEME["bg"],
                    "borderBottom": "1px solid #e5e7eb",
                },
            ),

            # Filters row
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Date Range", className="label",
                                    style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "6px"}),
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
                        style={"background": THEME["card"], "padding": "10px", "borderRadius": "10px"},
                    ),
                    html.Div(
                        [
                            html.Div("Quick Range", className="label",
                                    style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "6px"}),
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
                                labelStyle={"marginRight": "10px", "display": "inline-block"},
                            ),
                        ],
                        className="filter-block",
                        style={"background": THEME["card"], "padding": "10px", "borderRadius": "10px"},
                    ),
                    html.Div(
                        [
                            html.Div("Region", className="label",
                                    style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "6px"}),
                            dcc.Dropdown(
                                id="region-dd",
                                options=[{"label": r, "value": r} for r in sorted(fact["Region"].dropna().unique())],
                                multi=True,
                                placeholder="All",
                            ),
                        ],
                        className="filter-block",
                        style={"background": THEME["card"], "padding": "10px", "borderRadius": "10px"},
                    ),
                    html.Div(
                        [
                            html.Div("Category", className="label",
                                    style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "6px"}),
                            dcc.Dropdown(
                                id="category-dd",
                                options=[{"label": c, "value": c} for c in sorted(fact["Category"].dropna().unique())],
                                multi=True,
                                placeholder="All",
                            ),
                        ],
                        className="filter-block",
                        style={"background": THEME["card"], "padding": "10px", "borderRadius": "10px"},
                    ),
                    html.Div(
                        [
                            html.Div("Segment", className="label",
                                    style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "6px"}),
                            dcc.Dropdown(
                                id="segment-dd",
                                options=[{"label": s, "value": s} for s in sorted(fact["Segment"].dropna().unique())],
                                multi=True,
                                placeholder="All",
                            ),
                        ],
                        className="filter-block",
                        style={"background": THEME["card"], "padding": "10px", "borderRadius": "10px"},
                    ),
                ],
                className="filters-row",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1.2fr 1fr 1fr 1fr 1fr",
                    "gap": "10px",
                    "padding": "10px 14px",
                    "background": THEME["bg"],
                },
            ),

            # KPI row
            html.Div(
                [
                    kpi_card("Sales", "$0", _id="kpi-sales"),
                    kpi_card("Profit", "$0", _id="kpi-profit"),
                    kpi_card("Orders", "0", _id="kpi-orders"),
                    kpi_card("Margin", "0.0%", _id="kpi-margin"),
                ],
                className="kpi-row",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(4, 1fr)",
                    "gap": "10px",
                    "padding": "8px 14px",
                    "background": THEME["bg"],
                },
            ),

            # Charts grid (no scroll; fixed heights)
            html.Div(
                [
                    dcc.Graph(
                        id="ts-sales-profit",
                        config={"displaylogo": False},
                        style={"height": "280px", "gridArea": "ts"},
                    ),
                    dcc.Graph(
                        id="bar-category",
                        config={"displaylogo": False},
                        style={"height": "250px", "gridArea": "bar"},
                    ),
                    dcc.Graph(
                        id="heatmap-region-category",
                        config={"displaylogo": False},
                        style={"height": "250px", "gridArea": "heat"},
                    ),
                    dcc.Graph(
                        id="top-products",
                        config={"displaylogo": False},
                        style={"height": "420px", "gridArea": "top"},
                    ),
                ],
                className="charts-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "2fr 2fr",
                    "gridTemplateRows": "480px 400px",
                    "gridTemplateAreas": '"ts top" "bar heat"',
                    "gap": "10px",
                    "padding": "10px 14px",
                    "background": THEME["bg"],
                    # "height": "calc(100vh - 60px - 110px - 120px)",  # header + filters + kpis
                    "overflow": "hidden",
                },
            ),
        ],
        className="app",
        style={
            "fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial",
            "height": "100vh",
            "overflow": "hidden",
            "backgroundColor": THEME["bg"],
            # body margin reset can't be done here; ensure your page CSS or index sets body { margin: 0 }
        },
    )

    # ---------- Callbacks ----------

    # Quick range ➜ updates date picker
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
            # quarter start based on end date
            q = (end.month - 1) // 3 + 1
            start = pd.Timestamp(end.year, 3 * (q - 1) + 1, 1)
        elif preset == "ytd":
            start = pd.Timestamp(end.year, 1, 1)
        elif preset == "all":
            start = min_dt
        else:
            start = min_dt
        # clamp
        start = max(start, min_dt)
        end = min(end, max_dt)
        return start, end

    @app.callback(
        Output("kpi-sales", "children"),
        Output("kpi-profit", "children"),
        Output("kpi-orders", "children"),
        Output("kpi-margin", "children"),
        Output("ts-sales-profit", "figure"),
        Output("bar-category", "figure"),
        Output("heatmap-region-category", "figure"),
        Output("top-products", "figure"),
        Output("context-subtitle", "children"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("region-dd", "value"),
        Input("category-dd", "value"),
        Input("segment-dd", "value"),
    )
    def update_all(start, end, regions_v, cats_v, segs_v):
        # Filter fact
        f = apply_filters(fact, start, end, regions_v, cats_v, segs_v)
        start_dt, end_dt = pd.to_datetime(start), pd.to_datetime(end)

        # Handle empty frame
        if f.empty:
            subtitle = f"{start_dt.date()} → {end_dt.date()} | (No data for current filters)"
            return (
                "$0",
                "$0",
                "0",
                "0.0%",
                empty_fig("Monthly Sales & Profit"),
                empty_fig("Sales by Category"),
                empty_fig("Sales Heatmap: Region × Category"),
                empty_fig("Top 10 Products by Profit"),
                subtitle,
            )

        # ---------- KPIs ----------
        total_sales = float(f["Sales"].sum())
        total_profit = float(f["Profit"].sum())
        orders = int(f["Order ID"].nunique())
        margin = (total_profit / total_sales) if total_sales else 0.0

        # Period deltas (use monthly mart if no dim filters; compare against previous equal-length window)
        delta_sales = delta_profit = delta_margin = None
        try:
            window_days = max((end_dt - start_dt).days, 1)
            prev_end = start_dt - pd.Timedelta(days=1)
            prev_start = prev_end - pd.Timedelta(days=window_days)

            if _no_dim_filters(regions_v, cats_v, segs_v):
                m_curr = monthly[(monthly["Order Month"] >= start_dt) & (monthly["Order Month"] <= end_dt)]
                m_prev = monthly[(monthly["Order Month"] >= prev_start) & (monthly["Order Month"] <= prev_end)]
                curr_sales = float(m_curr.get("Total_Sales", pd.Series()).sum())
                curr_profit = float(m_curr.get("Total_Profit", pd.Series()).sum())
                prev_sales = float(m_prev.get("Total_Sales", pd.Series()).sum()) or 0.0
                prev_profit = float(m_prev.get("Total_Profit", pd.Series()).sum()) or 0.0
            else:
                # fallback on filtered data
                m_curr = f
                m_prev = fact[(fact["Order Date"] >= prev_start) & (fact["Order Date"] <= prev_end)]
                curr_sales = float(m_curr["Sales"].sum())
                curr_profit = float(m_curr["Profit"].sum())
                prev_sales = float(m_prev["Sales"].sum()) or 0.0
                prev_profit = float(m_prev["Profit"].sum()) or 0.0

            curr_margin = (curr_profit / curr_sales) if curr_sales else 0.0
            prev_margin = (prev_profit / prev_sales) if prev_sales else 0.0

            delta_sales = compute_period_delta(curr_sales, prev_sales)
            delta_profit = compute_period_delta(curr_profit, prev_profit)
            delta_margin = compute_period_delta(curr_margin, prev_margin)
        except Exception:
            pass  # keep deltas as None if anything odd occurs

        k1 = f"${total_sales:,.0f}"
        k2 = f"${total_profit:,.0f}"
        k3 = f"{orders:,d}"
        k4 = f"{margin:.1%}"

        # ---------- Time Series (Area) ----------
        if _no_dim_filters(regions_v, cats_v, segs_v):
            ts = monthly[
                (monthly["Order Month"] >= start_dt) & (monthly["Order Month"] <= end_dt)
            ].sort_values("Order Month")
            if {"Total_Sales", "Total_Profit"}.issubset(ts.columns):
                fig_ts = go.Figure()
                fig_ts.add_trace(
                    go.Scatter(
                        x=ts["Order Month"],
                        y=ts["Total_Sales"],
                        mode="lines",
                        name="Sales",
                        fill="tozeroy",
                    )
                )
                fig_ts.add_trace(
                    go.Scatter(
                        x=ts["Order Month"],
                        y=ts["Total_Profit"],
                        mode="lines",
                        name="Profit",
                        fill="tozeroy",
                    )
                )
                fig_ts.update_layout(
                    title="Monthly Sales & Profit (pre-aggregated)",
                    margin=dict(l=10, r=10, t=40, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    colorway=COLORWAY,
                )
            else:
                # fallback (columns named differently)
                fig_ts = px.area(
                    ts, x="Order Month", y=[c for c in ts.columns if "Total" in c], title="Monthly Sales & Profit"
                )
        else:
            ts = (
                f.groupby("Order Month")
                .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
                .reset_index()
                .sort_values("Order Month")
            )
            fig_ts = px.area(ts, x="Order Month", y=["Sales", "Profit"], title="Monthly Sales & Profit (filtered)")
            fig_ts.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                colorway=COLORWAY,
            )

        # Peak annotation
        try:
            peak_idx = ts["Sales" if "Sales" in ts.columns else "Total_Sales"].idxmax()
            peak_x = ts.loc[peak_idx, "Order Month"]
            peak_y = ts.loc[peak_idx, "Sales" if "Sales" in ts.columns else "Total_Sales"]
            fig_ts.add_annotation(
                x=peak_x,
                y=peak_y,
                text=f"Peak: {peak_y:,.0f}",
                showarrow=True,
                arrowhead=1,
                yshift=20,
            )
        except Exception:
            pass

        # ---------- Category Contribution (Horizontal Bar) ----------
        cat = (
            f.groupby("Category")
            .agg(Sales=("Sales", "sum"))
            .reset_index()
            .sort_values("Sales", ascending=True)
        )
        fig_bar = px.bar(
            cat, x="Sales", y="Category", orientation="h", title="Sales by Category", text="Sales", color="Category"
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False,
            colorway=COLORWAY,
        )
        fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)

        # ---------- Region × Category Heatmap (with labels) ----------
        heat = (
            f.pivot_table(values="Sales", index="Region", columns="Category", aggfunc="sum", fill_value=0)
            .reset_index()
            .melt(id_vars="Region", var_name="Category", value_name="Sales")
        )
        fig_heat = px.density_heatmap(
            heat,
            x="Category",
            y="Region",
            z="Sales",
            color_continuous_scale="Blues",
            title="Sales Heatmap: Region × Category",
        )
        # Add text labels
        fig_heat.update_traces(
            hovertemplate="Region=%{y}<br>Category=%{x}<br>Sales=%{z:,.0f}<extra></extra>",
            showscale=True,
        )
        fig_heat.update_layout(margin=dict(l=10, r=10, t=40, b=10))

        # ---------- Top Products (Horizontal Bar) ----------
        top = (
            f.groupby("Product Name")
            .agg(Profit=("Profit", "sum"))
            .reset_index()
            .sort_values("Profit", ascending=True)
            .tail(10)
        )
        fig_top = px.bar(
            top, x="Profit", y="Product Name", orientation="h", title="Top 10 Products by Profit", text="Profit"
        )
        fig_top.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            colorway=COLORWAY,
            showlegend=False,
        )
        fig_top.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)

        # ---------- Subtitle Context ----------
        active_filters = []
        if regions_v: active_filters.append(f"Regions: {', '.join(regions_v)}")
        if cats_v:    active_filters.append(f"Categories: {', '.join(cats_v)}")
        if segs_v:    active_filters.append(f"Segments: {', '.join(segs_v)}")
        filters_txt = " | ".join(active_filters) if active_filters else "All Regions • All Categories • All Segments"
        subtitle = f"{start_dt.date()} → {end_dt.date()}  |  {filters_txt}"

        # Return
        return k1, k2, k3, k4, fig_ts, fig_bar, fig_heat, fig_top, subtitle

    return app


if __name__ == "__main__":
    from ..config import DATA_CURATED
    app = make_app(DATA_CURATED)
    app.run(debug=True)