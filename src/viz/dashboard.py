import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from pathlib import Path
from dash.exceptions import PreventUpdate

# Load curated CSVs for the app (lightweight for demo)

def load_curated(curated_dir: Path):
    fact = pd.read_csv(curated_dir / 'fact_orders.csv', parse_dates=['Order Date','Ship Date','Order Month'])
    monthly = pd.read_csv(curated_dir / 'mart_orders_monthly.csv', parse_dates=['Order Month'])
    return fact, monthly

def make_app(curated_dir: Path):
    fact, monthly = load_curated(curated_dir)

    app = Dash(__name__, suppress_callback_exceptions=True)

    # Use monthly pre-aggregated data only when no dimensional filters are applied
    def _no_dim_filters(regions, cats, segs):
        return (not regions) and (not cats) and (not segs)


    regions = sorted(fact['Region'].dropna().unique())
    categories = sorted(fact['Category'].dropna().unique())
    segments = sorted(fact['Segment'].dropna().unique())

    app.layout = html.Div([
        html.H2("Superstore Performance Dashboard"),
        html.P("Dynamic filters: time range, region, category, segment"),

        html.Div([
            dcc.DatePickerRange(
                id = 'date-range',
                start_date=fact['Order Date'].min(),
                end_date=fact['Order Date'].max()
            ),
            dcc.Dropdown(options=[{'label': r, 'value': r} for r in regions], id = 'region-dd', multi=True, placeholder='Region'),
            dcc.Dropdown(options=[{'label': c, 'value': c} for c in categories], id='category-dd', multi=True, placeholder='Category'),
            dcc.Dropdown(options=[{'label': s, 'value': s} for s in segments], id='segment-dd', multi=True, placeholder='Segment')
        ], style={'display':'grid', 'gridTemplateColumns':'1fr 1fr 1fr 1fr','gap':'10px'}),
        
        html.Hr(),

        # KPI cards (simple)
        html.Div([
            html.Div(id='kpi-sales', className='kpi'),
            html.Div(id='kpi-profit', className='kpi'),
            html.Div(id='kpi-orders', className='kpi'),
            html.Div(id='kpi-margin', className='kpi'),
        ], style={'display':'grid','gridTemplateColumns':'repeat(4, 1fr)','gap':'10px'}),

        html.Hr(),

        # Time Series
        dcc.Graph(id = 'ts-sales-profit'),

        # Contribution bars
        dcc.Graph(id = 'bar-category'),

        # Heatmap: Region x Category by Sales
        dcc.Graph(id = 'heatmap-region-category'),

        # Top products table (as bar)
        dcc.Graph(id = 'top-products')
    ], style={'padding': '12px'})
    

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

    
    @app.callback(
        Output('kpi-sales','children'), 
        Output('kpi-profit','children'), 
        Output('kpi-orders','children'), 
        Output('kpi-margin','children'),
        Output('ts-sales-profit','figure'), 
        Output('bar-category','figure'), 
        Output('heatmap-region-category','figure'), 
        Output('top-products','figure'),
        Input('date-range','start_date'), 
        Input('date-range','end_date'),
        Input('region-dd','value'), 
        Input('category-dd','value'), 
        Input('segment-dd','value')
    )
    def update_all(start, end, regions_v, cats_v, segs_v):
        f = apply_filters(fact, start, end, regions_v, cats_v, segs_v)

        total_sales = f['Sales'].sum()
        total_profit = f['Profit'].sum()
        orders = f['Order ID'].nunique()
        margin = (total_profit/total_sales) if total_sales else 0
        k1 = html.H4(f"Sales: ${total_sales:,.0f}")
        k2 = html.H4(f"Profit: ${total_profit:,.0f}")
        k3 = html.H4(f"Orders: ${orders:,.0f}")
        k4 = html.H4(f"Margin: ${margin:.1%}")
        if f.empty:
            k1 = html.H4("Sales: $0")
            k2 = html.H4("Profit: $0")
            k3 = html.H4("Orders: 0")
            k4 = html.H4("Margin: 0.0%")
            empty_ts = px.line(title='Monthly Sales & Profit (no data)')
            empty_bar = px.bar(title='Sales by Category (no data)')
            empty_heat = px.density_heatmap(title='Sales Heatmap: Region x Category (no data)')
            empty_top = px.bar(title='Top 10 Products by Profit (no data)')
            return k1, k2, k3, k4, empty_ts, empty_bar, empty_heat, empty_top

        # # Time Series
        # ts = f.groupby('Order Month').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
        # fig_ts = px.line(ts, x='Order Month', y=['Sales','Profit'], title='Monthly Sales & Profit')

        # --- Time series ---
        if _no_dim_filters(regions_v, cats_v, segs_v):
            # Use pre-aggregated monthly mart (fast path)
            ts = monthly[
                (monthly['Order Month'] >= pd.to_datetime(start)) &
                (monthly['Order Month'] <= pd.to_datetime(end))
            ].sort_values('Order Month')

            # The mart has Total_Sales / Total_Profit columns
            fig_ts = px.line(
                ts,
                x='Order Month',
                y=['Total_Sales','Total_Profit'],
                title='Monthly Sales & Profit (pre-aggregated)'
            )
            fig_ts.update_traces(mode='lines+markers')
        else:
            # Fall back to on-the-fly aggregation when filters are applied
            ts = (
                f.groupby('Order Month')
                .agg(Sales=('Sales','sum'), Profit=('Profit','sum'))
                .reset_index()
                .sort_values('Order Month')
            )
            fig_ts = px.line(
                ts,
                x='Order Month',
                y=['Sales','Profit'],
                title='Monthly Sales & Profit (filtered)'
            )
            fig_ts.update_traces(mode='lines+markers')

        
        # Category contribution
        cat = f.groupby('Category').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
        fig_bar = px.bar(cat, x='Category', y='Sales', color='Category', title='Sales by Category', text='Sales')

        # Heatmap Region x Category
        heat = f.pivot_table(values='Sales', index='Region', columns='Category', aggfunc='sum', fill_value=0)
        heat = heat.reset_index().melt(id_vars='Region', var_name='Category', value_name='Sales')
        fig_heat = px.density_heatmap(heat, x='Category', y='Region', z='Sales', color_continuous_scale='Blues', title='Sales Heatmap: Region x Category')

        # Top products
        top = f.groupby('Product Name').agg(Profit=('Profit','sum')).reset_index().sort_values('Profit', ascending=False).head(10)
        fig_top = px.bar(top, x='Profit', y='Product Name', orientation='h', title='Top 10 Products by Profit')

        return k1, k2, k3, k4, fig_ts, fig_bar, fig_heat, fig_top
    
    return app


if __name__ == "__main__":
    from ..config import DATA_CURATED
    app = make_app(DATA_CURATED)
    app.run(debug=True)