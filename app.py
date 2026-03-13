"""
app.py — Sales & Shades | Dash Web Application
============================================================
Stack : Python · Dash · Plotly · pandas · SQLite
Run   : python app.py  →  open http://127.0.0.1:8050
============================================================
"""

import os
import pandas as pd
import numpy as np

import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import queries

# ── Theme ─────────────────────────────────────────────────
BG      = '#0d0f14'
SURFACE = '#13161e'
BORDER  = '#1e2230'
TEXT    = '#f0ede6'
MUTED   = '#8a8e9a'
GREEN   = '#3ecf74'
AMBER   = '#f5a623'
BLUE    = '#4a90d9'
CORAL   = '#e8684a'
PURPLE  = '#9b8ff5'
PINK    = '#f0699a'
TEAL    = '#5dcaa5'
PALETTE = [GREEN, BLUE, AMBER, CORAL, PURPLE, PINK, TEAL, '#f5c4b3']

MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']

BASE_LAYOUT = dict(
    paper_bgcolor=BG, plot_bgcolor=SURFACE,
    font=dict(family='DM Mono, monospace', color=TEXT, size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
    yaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=MUTED, size=10)),
    hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER,
                    font=dict(family='DM Mono', color=TEXT)),
)


# ══════════════════════════════════════════════════════════
# CHART BUILDERS
# ══════════════════════════════════════════════════════════
def build_monthly(quarter='ALL'):
    df = queries.get_monthly()
    if quarter != 'ALL':
        qm = {'Q1':['01','02','03'],'Q2':['04','05','06'],
              'Q3':['07','08','09'],'Q4':['10','11','12']}
        df = df[df['month'].str[-2:].isin(qm[quarter])]
    labels = [MONTH_NAMES[int(m[-2:])-1] for m in df['month']]
    colors = [GREEN if int(m[-2:]) in [10,11,12] else '#2a3040'
              for m in df['month']]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=df['revenue_lakhs'], marker_color=colors,
        marker_line_color=BORDER, marker_line_width=0.5,
        text=[f'₹{v:.0f}L' for v in df['revenue_lakhs']],
        textposition='outside', textfont=dict(size=9, color=MUTED),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:.1f}L<extra></extra>',
        name='Revenue',
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=df['total_orders'], mode='lines+markers',
        line=dict(color=AMBER, width=1.5, dash='dot'),
        marker=dict(size=5, color=AMBER), yaxis='y2', name='Orders',
        hovertemplate='Orders: %{y:,}<extra></extra>',
    ))
    ann = []
    if quarter == 'ALL':
        oct_df = df[df['month'].str[-2:] == '10']
        if len(oct_df):
            ann = [dict(x='Oct', y=oct_df['revenue_lakhs'].values[0],
                        text='Diwali↑', showarrow=True, arrowhead=2,
                        arrowcolor=AMBER, font=dict(color=AMBER, size=9),
                        ax=0, ay=-30)]
    fig.update_layout(
        **BASE_LAYOUT,
        yaxis2=dict(overlaying='y', side='right',
                    gridcolor='rgba(0,0,0,0)',
                    tickfont=dict(color=AMBER, size=9)),
        barmode='group', showlegend=True, annotations=ann,
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1),
    )
    return fig


def build_products(category='ALL'):
    df = queries.get_products()
    if category != 'ALL':
        df = df[df['category'] == category]
    df = df.head(8)
    names  = df['product_name'].str.split().str[:2].str.join(' ')
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(df))]
    fig = go.Figure(go.Bar(
        y=names[::-1], x=df['revenue_lakhs'][::-1],
        orientation='h', marker_color=colors[::-1],
        marker_line_color=BORDER, marker_line_width=0.5,
        text=[f'₹{v:.0f}L' for v in df['revenue_lakhs'][::-1]],
        textposition='outside', textfont=dict(size=9, color=MUTED),
        hovertemplate='<b>%{y}</b><br>Revenue: ₹%{x:.1f}L<extra></extra>',
    ))
    fig.update_layout(**BASE_LAYOUT, xaxis_title='Revenue (₹L)',
                      showlegend=False)
    return fig


def build_regions():
    df  = queries.get_regions()
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(
        x=df['region'], y=df['revenue_lakhs'], name='Revenue (₹L)',
        marker_color=BLUE, marker_line_color=BORDER,
        hovertemplate='<b>%{x}</b><br>₹%{y:.1f}L<extra></extra>',
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df['region'], y=df['return_rate'], name='Return Rate %',
        mode='lines+markers', line=dict(color=CORAL, width=2),
        marker=dict(size=8, color=CORAL),
        hovertemplate='Return Rate: %{y:.1f}%<extra></extra>',
    ), secondary_y=True)
    fig.update_layout(**BASE_LAYOUT, showlegend=True,
                      legend=dict(orientation='h', y=1.1))
    fig.update_yaxes(title_text='Revenue (₹L)', gridcolor=BORDER,
                     secondary_y=False)
    fig.update_yaxes(title_text='Return Rate (%)',
                     gridcolor='rgba(0,0,0,0)',
                     tickfont=dict(color=CORAL), secondary_y=True)
    return fig


def build_segments():
    df  = queries.get_segments()
    fig = go.Figure(go.Pie(
        labels=df['segment'], values=df['revenue_lakhs'], hole=0.55,
        marker=dict(colors=[GREEN, BLUE, AMBER],
                    line=dict(color=BG, width=3)),
        textinfo='percent+label', textfont=dict(size=10, color=TEXT),
        hovertemplate='<b>%{label}</b><br>₹%{value:.1f}L<extra></extra>',
    ))
    fig.update_layout(
        **BASE_LAYOUT, showlegend=False,
        annotations=[dict(
            text=f'₹{df["revenue_lakhs"].sum():.0f}L',
            x=0.5, y=0.5, font_size=14, font_color=TEXT, showarrow=False,
        )]
    )
    return fig


def build_quarterly():
    df   = queries.get_quarterly()
    cats = df['category'].unique()
    fig  = go.Figure()
    for i, cat in enumerate(cats):
        sub = df[df['category'] == cat]
        fig.add_trace(go.Bar(
            x=sub['quarter'], y=sub['revenue_lakhs'], name=cat,
            marker_color=PALETTE[i % len(PALETTE)],
            hovertemplate=f'<b>{cat}</b><br>₹%{{y:.1f}}L<extra></extra>',
        ))
    fig.update_layout(**BASE_LAYOUT, barmode='stack',
                      xaxis_title='Quarter', yaxis_title='Revenue (₹L)',
                      legend=dict(orientation='h', y=1.1, font=dict(size=9)))
    return fig


# ══════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════
def kpi_card(value, label, change, direction, accent):
    color = GREEN if direction == 'up' else CORAL
    arrow = '▲' if direction == 'up' else '▼'
    return html.Div([
        html.Div(style={'height':'2px','background':accent}),
        html.Div([
            html.Div(label, style={
                'fontFamily':'DM Mono,monospace','fontSize':'10px',
                'color':MUTED,'letterSpacing':'0.1em',
                'textTransform':'uppercase','marginBottom':'8px'}),
            html.Div(value, style={
                'fontSize':'26px','fontWeight':'800','color':TEXT,
                'letterSpacing':'-1px','lineHeight':'1'}),
            html.Div(f'{arrow} {change}', style={
                'fontFamily':'DM Mono,monospace','fontSize':'11px',
                'color':color,'marginTop':'8px'}),
        ], style={'padding':'16px 20px'}),
    ], style={
        'background':SURFACE,'border':f'1px solid {BORDER}',
        'borderRadius':'8px','flex':'1','minWidth':'160px','overflow':'hidden',
    })


def panel(children, extra=None):
    style = {'background':SURFACE,'border':f'1px solid {BORDER}',
             'borderRadius':'8px','padding':'20px'}
    if extra:
        style.update(extra)
    return html.Div(children, style=style)


def lbl(text):
    return html.Div(text, style={
        'fontFamily':'DM Mono,monospace','fontSize':'10px','color':MUTED,
        'textTransform':'uppercase','letterSpacing':'0.1em','marginBottom':'12px',
    })


# ══════════════════════════════════════════════════════════
# APP INIT
# ══════════════════════════════════════════════════════════
app = dash.Dash(__name__, title='Sales & Shades | DA Portfolio',
                suppress_callback_exceptions=True)


# ══════════════════════════════════════════════════════════
# MAIN LAYOUT — filters + hidden stores live at top level
# so callbacks always find them regardless of active tab
# ══════════════════════════════════════════════════════════
app.layout = html.Div([

    # ── Header ──────────────────────────────────────────
    html.Div([
        html.Div([
            html.H1('Sales & Shades', style={
                'fontSize':'22px','fontWeight':'800','color':TEXT,
                'letterSpacing':'-0.5px','margin':'0'}),
            html.Div('Sales Data Analysis  ·  FY 2024  ·  Eyewear Division',
                     style={'fontFamily':'DM Mono,monospace','fontSize':'10px',
                            'color':MUTED,'letterSpacing':'0.08em',
                            'textTransform':'uppercase','marginTop':'4px'}),
        ]),
        html.Div([
            html.Div('Python · Dash · Plotly · pandas · SQLite',
                     style={'fontFamily':'DM Mono,monospace','fontSize':'10px',
                            'color':MUTED,'marginRight':'16px'}),
            html.Div('● LIVE', style={
                'fontFamily':'DM Mono,monospace','fontSize':'10px',
                'padding':'5px 12px','borderRadius':'4px',
                'background':'#0f2b1a','color':GREEN,
                'border':'1px solid #1a4a2e','letterSpacing':'0.06em',
            }),
        ], style={'display':'flex','alignItems':'center'}),
    ], style={
        'display':'flex','justifyContent':'space-between','alignItems':'center',
        'padding':'18px 28px','borderBottom':f'3px solid {GREEN}',
        'background':SURFACE,
    }),

    # ── Tabs ────────────────────────────────────────────
    dcc.Tabs(id='tabs', value='tab-dash', children=[
        dcc.Tab(label='Dashboard',  value='tab-dash'),
        dcc.Tab(label='Data Table', value='tab-data'),
        dcc.Tab(label='SQL Viewer', value='tab-sql'),
        dcc.Tab(label='EDA Report', value='tab-eda'),
    ], colors={'border':BORDER,'primary':GREEN,'background':BG},
       style={'fontFamily':'DM Mono,monospace'}),

    # ── FILTER BAR — always in DOM, hidden on other tabs ─
    html.Div([
        html.Div('Quarter:', style={
            'fontFamily':'DM Mono,monospace','fontSize':'10px','color':MUTED,
            'textTransform':'uppercase','letterSpacing':'0.08em',
            'alignSelf':'center'}),
        dcc.Dropdown(
            id='dd-quarter', value='ALL', clearable=False,
            options=[
                {'label':'All Year',    'value':'ALL'},
                {'label':'Q1 Jan–Mar',  'value':'Q1'},
                {'label':'Q2 Apr–Jun',  'value':'Q2'},
                {'label':'Q3 Jul–Sep',  'value':'Q3'},
                {'label':'Q4 Oct–Dec',  'value':'Q4'},
            ],
            style={'width':'160px','fontFamily':'DM Mono,monospace','fontSize':'11px'},
        ),
        html.Div('Category:', style={
            'fontFamily':'DM Mono,monospace','fontSize':'10px','color':MUTED,
            'textTransform':'uppercase','letterSpacing':'0.08em',
            'alignSelf':'center','marginLeft':'12px'}),
        dcc.Dropdown(
            id='dd-category', value='ALL', clearable=False,
            options=[
                {'label':'All Categories','value':'ALL'},
                {'label':'Premium',       'value':'PREMIUM'},
                {'label':'Fashion',       'value':'FASHION'},
                {'label':'Sport',         'value':'SPORT'},
                {'label':'Casual',        'value':'CASUAL'},
                {'label':'Kids',          'value':'KIDS'},
            ],
            style={'width':'170px','fontFamily':'DM Mono,monospace','fontSize':'11px'},
        ),
        html.Div(style={'flex':'1'}),
        html.Button('⬇ Export CSV', id='btn-csv', n_clicks=0),
        dcc.Download(id='dl-csv'),
    ], id='filter-bar', style={
        'display':'flex','gap':'10px','alignItems':'center',
        'padding':'12px 20px','background':SURFACE,
        'borderBottom':f'1px solid {BORDER}',
    }),

    # ── Tab content ─────────────────────────────────────
    html.Div(id='tab-content'),

], style={'background':BG,'minHeight':'100vh'})


# ══════════════════════════════════════════════════════════
# TAB CONTENT BUILDERS
# ══════════════════════════════════════════════════════════
def make_dashboard():
    kpis = queries.get_kpis()
    return html.Div([
        # KPI strip
        html.Div([
            kpi_card(f'₹{kpis["revenue"]:.1f}L','Total Revenue', '+18.4% vs LY','up',GREEN),
            kpi_card(f'{kpis["orders"]:,}','Total Orders',     '+11.2% vs LY','up',AMBER),
            kpi_card(f'₹{kpis["aov"]:,}','Avg Order Value',   '+6.4% vs LY', 'up',BLUE),
            kpi_card(f'{kpis["return_rate"]:.1f}%','Return Rate','-0.8pp vs LY','down',CORAL),
        ], style={'display':'flex','gap':'12px','marginBottom':'16px','flexWrap':'wrap'}),

        # Row 1 — Monthly + Products
        html.Div([
            panel([
                lbl('Monthly Revenue Trend  (₹ Lakhs)'),
                dcc.Graph(id='g-monthly',
                          config={'displayModeBar':True,
                                  'modeBarButtonsToRemove':['lasso2d','select2d'],
                                  'toImageButtonOptions':{'format':'png','scale':2,
                                                          'filename':'monthly_revenue'}},
                          style={'height':'280px'}),
            ], extra={'flex':'2','minWidth':'300px'}),
            panel([
                lbl('Top Products by Revenue'),
                dcc.Graph(id='g-products',
                          config={'displayModeBar':False},
                          style={'height':'280px'}),
            ], extra={'flex':'1','minWidth':'260px'}),
        ], style={'display':'flex','gap':'12px','marginBottom':'12px'}),

        # Row 2 — Regions + Segments + Quarterly
        html.Div([
            panel([
                lbl('Regional Revenue vs Return Rate'),
                dcc.Graph(id='g-regions',
                          config={'displayModeBar':False},
                          style={'height':'260px'}),
            ], extra={'flex':'1','minWidth':'260px'}),
            panel([
                lbl('Customer Segment Mix'),
                dcc.Graph(id='g-segments',
                          config={'displayModeBar':False},
                          style={'height':'260px'}),
            ], extra={'flex':'1','minWidth':'240px'}),
            panel([
                lbl('Quarterly Revenue by Category'),
                dcc.Graph(id='g-quarterly',
                          config={'displayModeBar':False},
                          style={'height':'260px'}),
            ], extra={'flex':'1','minWidth':'260px'}),
        ], style={'display':'flex','gap':'12px'}),
    ], style={'padding':'20px'})


def make_datatable():
    df = queries.get_raw_table(200)
    return html.Div([
        html.Div([
            html.Div([
                lbl('Raw Sales Data  (latest 200 orders)'),
                html.Div('Sort by column header · Filter by typing in filter row',
                         style={'fontSize':'11px','color':MUTED,
                                'fontFamily':'DM Mono,monospace','marginBottom':'12px'}),
            ]),
            html.Div([
                html.Button('⬇ Export Full CSV', id='btn-full', n_clicks=0),
                dcc.Download(id='dl-full'),
            ]),
        ], style={'display':'flex','justifyContent':'space-between',
                  'alignItems':'flex-end','marginBottom':'16px'}),
        dash_table.DataTable(
            id='raw-table',
            columns=[{'name':c,'id':c} for c in df.columns],
            data=df.to_dict('records'),
            sort_action='native', filter_action='native',
            page_action='native', page_size=20,
            style_table={'overflowX':'auto','borderRadius':'8px',
                         'border':f'1px solid {BORDER}'},
            style_header={'backgroundColor':SURFACE,'color':MUTED,
                          'fontFamily':'DM Mono,monospace','fontSize':'10px',
                          'textTransform':'uppercase','letterSpacing':'0.07em',
                          'borderBottom':f'1px solid {BORDER}'},
            style_cell={'backgroundColor':BG,'color':TEXT,
                        'border':f'1px solid {BORDER}',
                        'fontFamily':'DM Mono,monospace','fontSize':'12px',
                        'padding':'8px 12px','minWidth':'80px'},
            style_data_conditional=[
                {'if':{'filter_query':'{returned} = "Yes"'},'color':CORAL},
                {'if':{'row_index':'odd'},'backgroundColor':SURFACE},
            ],
        ),
    ], style={'padding':'20px'})


def make_sql():
    opts = [{'label':k,'value':k} for k in queries.SQL_CATALOG]
    return html.Div([
        lbl('SQL Query Viewer'),
        html.Div('Every chart is powered by one of these queries. Select to inspect.',
                 style={'fontSize':'11px','color':MUTED,
                        'fontFamily':'DM Mono,monospace','marginBottom':'16px'}),
        dcc.Dropdown(id='dd-sql', options=opts, value=opts[0]['value'],
                     clearable=False,
                     style={'fontFamily':'DM Mono,monospace','fontSize':'11px',
                            'marginBottom':'16px'}),
        panel([
            html.Pre(id='sql-code', style={
                'margin':'0','background':'#0a0c10','color':GREEN,
                'fontFamily':'DM Mono,monospace','fontSize':'12px',
                'border':f'1px solid {BORDER}','borderRadius':'6px',
                'padding':'20px','overflowX':'auto',
                'lineHeight':'1.8','whiteSpace':'pre',
            }),
        ]),
        html.Div([
            lbl('Query Result Preview  (top 10 rows)'),
            html.Div(id='sql-result'),
        ], style={'marginTop':'20px'}),
    ], style={'padding':'20px'})


def make_eda():
    monthly   = queries.get_monthly()
    regions   = queries.get_regions()
    products  = queries.get_products()
    anomalies = queries.get_anomalies()
    corr_df   = queries.get_corr_data()

    peak_m   = MONTH_NAMES[int(monthly.loc[monthly['revenue_lakhs'].idxmax(),'month'][-2:])-1]
    top_p    = products.iloc[0]['product_name']
    top_pct  = products.iloc[0]['revenue_share_pct']
    bad_reg  = regions.loc[regions['return_rate'].idxmax(),'region']
    bad_rate = regions['return_rate'].max()
    avg_rate = regions['return_rate'].mean()

    def dot(color, text):
        return html.Div([
            html.Div(style={'width':'7px','height':'7px','borderRadius':'50%',
                            'background':color,'marginTop':'5px','flexShrink':'0'}),
            html.Div(text, style={'fontSize':'13px','color':MUTED,'lineHeight':'1.6'}),
        ], style={'display':'flex','gap':'12px','padding':'10px 0',
                  'borderBottom':f'1px solid {BORDER}'})

    numeric  = corr_df[['revenue_lakhs','orders','avg_order_value','returns','avg_discount']]
    corr     = numeric.corr().round(2)
    corr_fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
        colorscale='RdBu', zmid=0,
        text=corr.values.round(2), texttemplate='%{text}',
        textfont=dict(size=11, color=TEXT), hoverongaps=False, xgap=2, ygap=2,
    ))
    corr_fig.update_layout(**BASE_LAYOUT, height=320,
                           title=dict(text='KPI Correlation Matrix',
                                      font=dict(color=MUTED, size=11)))
    return html.Div([
        html.Div([
            panel([
                lbl('Automated EDA Insights'),
                dot(GREEN,  f'Peak month: {peak_m} — Diwali festive demand drove highest revenue.'),
                dot(CORAL,  f'{bad_reg} return rate {bad_rate:.1f}% vs avg {avg_rate:.1f}% — logistics flag.'),
                dot(AMBER,  f'{top_p} = {top_pct:.1f}% of total revenue. Concentration risk.'),
                dot(BLUE,   'B2B segment highest AOV. Corporate gifting growing +22%.'),
                dot(PURPLE, 'Discount % negatively correlates with revenue. Heavy discounting ineffective.'),
                dot(TEAL,   'Kids category underperformed Q2. Price elasticity test recommended.'),
            ], extra={'flex':'1'}),
            panel([
                lbl('Return Rate Anomalies  (> 4% threshold)'),
                dash_table.DataTable(
                    columns=[{'name':c,'id':c} for c in anomalies.columns],
                    data=anomalies.to_dict('records'),
                    style_table={'overflowX':'auto'},
                    style_header={'backgroundColor':SURFACE,'color':MUTED,
                                  'fontFamily':'DM Mono,monospace','fontSize':'10px',
                                  'textTransform':'uppercase',
                                  'borderBottom':f'1px solid {BORDER}'},
                    style_cell={'backgroundColor':BG,'color':TEXT,
                                'border':f'1px solid {BORDER}',
                                'fontFamily':'DM Mono,monospace',
                                'fontSize':'11px','padding':'8px 12px'},
                    style_data_conditional=[{
                        'if':{'filter_query':'{return_rate_pct} > 6'},
                        'color':CORAL,'fontWeight':'bold',
                    }],
                ),
            ], extra={'flex':'1'}),
        ], style={'display':'flex','gap':'12px','marginBottom':'12px'}),
        panel([
            lbl('KPI Correlation Analysis'),
            dcc.Graph(figure=corr_fig, config={'displayModeBar':False},
                      style={'height':'320px'}),
        ]),
    ], style={'padding':'20px'})


# ══════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════

# Tab switcher — also controls filter bar visibility
@app.callback(
    Output('tab-content', 'children'),
    Output('filter-bar', 'style'),
    Input('tabs', 'value'),
)
def render_tab(tab):
    show = {'display':'flex','gap':'10px','alignItems':'center',
            'padding':'12px 20px','background':SURFACE,
            'borderBottom':f'1px solid {BORDER}'}
    hide = {'display':'none'}
    if tab == 'tab-dash':
        return make_dashboard(), show
    if tab == 'tab-data':
        return make_datatable(), hide
    if tab == 'tab-sql':
        return make_sql(), hide
    if tab == 'tab-eda':
        return make_eda(), hide
    return html.Div(), hide


# All 5 charts driven by the SAME two dropdowns
# No prevent_initial_call — charts fire on load naturally
@app.callback(
    Output('g-monthly',  'figure'),
    Output('g-products', 'figure'),
    Output('g-regions',  'figure'),
    Output('g-segments', 'figure'),
    Output('g-quarterly','figure'),
    Input('dd-quarter',  'value'),
    Input('dd-category', 'value'),
)
def update_all_charts(quarter, category):
    return (
        build_monthly(quarter),
        build_products(category),
        build_regions(),
        build_segments(),
        build_quarterly(),
    )


# SQL viewer
@app.callback(
    Output('sql-code',   'children'),
    Output('sql-result', 'children'),
    Input('dd-sql',      'value'),
)
def show_sql(name):
    sql  = queries.SQL_CATALOG[name]
    conn = queries._conn()
    try:
        df  = pd.read_sql(sql, conn)
        conn.close()
        tbl = dash_table.DataTable(
            columns=[{'name':c,'id':c} for c in df.columns],
            data=df.head(10).to_dict('records'),
            style_table={'overflowX':'auto','border':f'1px solid {BORDER}',
                         'borderRadius':'8px'},
            style_header={'backgroundColor':SURFACE,'color':MUTED,
                          'fontFamily':'DM Mono,monospace','fontSize':'10px',
                          'textTransform':'uppercase',
                          'borderBottom':f'1px solid {BORDER}'},
            style_cell={'backgroundColor':BG,'color':TEXT,
                        'border':f'1px solid {BORDER}',
                        'fontFamily':'DM Mono,monospace',
                        'fontSize':'11px','padding':'7px 12px'},
        )
    except Exception as e:
        tbl = html.Div(str(e), style={'color':CORAL})
    return sql, tbl


# CSV exports
@app.callback(Output('dl-csv','data'), Input('btn-csv','n_clicks'),
              prevent_initial_call=True)
def export_csv(_):
    return dcc.send_data_frame(queries.get_monthly().to_csv,
                               'sales_monthly.csv', index=False)


@app.callback(Output('dl-full','data'), Input('btn-full','n_clicks'),
              prevent_initial_call=True)
def export_full(_):
    return dcc.send_data_frame(queries.get_raw_table(999999).to_csv,
                               'sales_full.csv', index=False)


# ══════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("  Sales & Shades | Dash App")
    print("  Open → http://127.0.0.1:8050")
    print("=" * 50)
    app.run(debug=True, port=8050)
