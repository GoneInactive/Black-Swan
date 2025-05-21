import json
import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import datetime
import time
import os
import requests

def ensure_data_directory():
    """Create data directory if it doesn't exist and create placeholder files if needed"""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created data directory")
        
        placeholder_files = {
            'news.json': [
                {"time": "10:23 AM", "headline": "Welcome to TradeByte Terminal", "source": "System"}
            ],
            'strategy_stats.json': {
                "Strategy Name": "TradeByte Demo",
                "Return": "15.67%",
                "Sharpe": "1.85",
                "Drawdown": "-8.32%",
                "Win Rate": "62.5%",
                "Status": "ACTIVE"
            }
        }
        
        for filename, data in placeholder_files.items():
            with open(f'data/{filename}', 'w') as f:
                json.dump(data, f)
                
    for asset in CRYPTO_ASSETS:
        price_file = f'data/{asset.lower()}_prices.json'
        if not os.path.exists(price_file):
            now = datetime.datetime.now()
            timestamps = [(now - datetime.timedelta(hours=x)).strftime("%Y-%m-%d %H:%M:%S") 
                          for x in range(24, 0, -1)]
            
            base_price = 100.0  
            if asset == 'BTC':
                base_price = 65000.0
            elif asset == 'ETH':
                base_price = 3500.0
            elif asset == 'SOL':
                base_price = 125.0
            elif asset == 'LTC':
                base_price = 80.0
            elif asset == 'XRP':
                base_price = 0.55
            elif asset == 'ADA':
                base_price = 0.45
                
            import random
            prices = [base_price]
            for i in range(1, 24):
                change_pct = (random.random() - 0.5) * 0.02  
                prices.append(prices[-1] * (1 + change_pct))
                
            price_data = [{"timestamp": ts, asset: p} for ts, p in zip(timestamps, prices)]
            
            with open(price_file, 'w') as f:
                json.dump(price_data, f)
                print(f"Created placeholder price data for {asset}")

app = Dash(__name__)
app.title = "TradeByte Terminal - Bloomberg Style"

CRYPTO_ASSETS = ['BTC', 'ETH', 'SOL', 'LTC', 'XRP', 'ADA']
COMMODITIES = ['Gold', 'Silver', 'Oil', 'NatGas']
INDICES = ['SPX', 'NDX', 'DJI', 'RUT']
ensure_data_directory()

# API_KEY = '3659930e56ec414a958d717950a981ff'
# URL = 'https://newsapi.org/v2/top-headlines'

API_KEY = '3659930e56ec414a958d717950a981ff'
URL = 'https://newsapi.org/v2/top-headlines'

def fetch_headlines():
    params = {
        'country': 'us',
        'category': 'business',
        'apiKey': API_KEY
    }
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        headlines = [article['title'] for article in articles]
        return headlines
    else:
        print("Failed to fetch news.")
        return []

def load_news_data():
    """Load news data from local JSON file instead of API"""
    try:
        timestamp = time.time()
        formatted_time = time.strftime("%I:%M %p", time.localtime(timestamp))
        NEWS_DATA = [{"time": formatted_time, "headline": headline.split(' - ')[0], "source": headline.split(' - ')[1]} for headline in fetch_headlines()]
        return NEWS_DATA
    except Exception as e:
        print(e)


BLOOMBERG_BG = '#0f0f0f'  # Dark background
BLOOMBERG_TEXT = '#ff8c00'  # Bloomberg orange/amber
BLOOMBERG_HIGHLIGHT = '#ffcc00'  # Brighter highlight
BLOOMBERG_BORDER = '#333333'  # Dark borders
BLOOMBERG_POSITIVE = '#00ff00'  # Green for positive
BLOOMBERG_NEGATIVE = '#ff0000'  # Red for negative

STYLE = {
    'backgroundColor': BLOOMBERG_BG,
    'color': BLOOMBERG_TEXT,
    'fontFamily': 'Arial, sans-serif',
    'padding': '5px',
    'height': '100vh'
#    'overflow': 'hidden'
}

PANEL_STYLE = {
    'backgroundColor': '#1a1a1a',
    'padding': '5px',
    'border': f'1px solid {BLOOMBERG_BORDER}',
    'margin': '5px',
    'borderRadius': '0px'
}

GRAPH_STYLE = {
    'backgroundColor': '#1a1a1a',
    'padding': '5px',
    'border': f'1px solid {BLOOMBERG_BORDER}',
    'margin': '5px',
    'borderRadius': '0px'
}

NEWS_DATA = load_news_data()

app.layout = html.Div([
    html.Div([
        html.Div("TRADEBYTE TERMINAL", style={
            'color': BLOOMBERG_HIGHLIGHT,
            'fontWeight': 'bold',
            'fontSize': '18px',
            'display': 'inline-block',
            'marginRight': '20px'
        }),
        html.Div(id='datetime-display', style={
            'display': 'inline-block',
            'marginRight': '20px'
        }),
        html.Div("LIVE", style={
            'color': BLOOMBERG_POSITIVE,
            'display': 'inline-block',
            'marginRight': '20px',
            'fontWeight': 'bold'
        }),
        html.Div("CONNECTED", style={
            'color': BLOOMBERG_POSITIVE,
            'display': 'inline-block',
            'marginRight': '20px'
        }),
        html.Div("LAST UPDATE: ", id='last-update', style={
            'display': 'inline-block',
            'marginRight': '20px'
        }),
    ], style={
        'borderBottom': f'1px solid {BLOOMBERG_BORDER}',
        'paddingBottom': '5px',
        'marginBottom': '5px'
    }),
    
    # Main content area
    html.Div([
        # Left column - Market data and Strategy Performance
        html.Div([
            # Crypto prices
            html.Div([
                html.Div("CRYPTO", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                dash_table.DataTable(
                    id='crypto-table',
                    columns=[
                        {'name': 'Symbol', 'id': 'symbol'},
                        {'name': 'Price', 'id': 'price'},
                        {'name': 'Chg', 'id': 'change'},
                        {'name': '%Chg', 'id': 'pct_change'},
                        {'name': 'Volume', 'id': 'volume'}
                    ],
                    style_header={
                        'backgroundColor': BLOOMBERG_BG,
                        'color': BLOOMBERG_TEXT,
                        'fontWeight': 'bold',
                        'border': 'none'
                    },
                    style_cell={
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': 'none',
                        'padding': '2px 5px',
                        'fontSize': '12px'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{change} > 0',
                                'column_id': ['change', 'pct_change']
                            },
                            'color': BLOOMBERG_POSITIVE
                        },
                        {
                            'if': {
                                'filter_query': '{change} < 0',
                                'column_id': ['change', 'pct_change']
                            },
                            'color': BLOOMBERG_NEGATIVE
                        }
                    ]
                )
            ], style=PANEL_STYLE),
            
            # Commodities
            html.Div([
                html.Div("COMMODITIES", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                dash_table.DataTable(
                    id='commodities-table',
                    columns=[
                        {'name': 'Symbol', 'id': 'symbol'},
                        {'name': 'Price', 'id': 'price'},
                        {'name': 'Chg', 'id': 'change'},
                        {'name': '%Chg', 'id': 'pct_change'}
                    ],
                    style_header={
                        'backgroundColor': BLOOMBERG_BG,
                        'color': BLOOMBERG_TEXT,
                        'fontWeight': 'bold',
                        'border': 'none'
                    },
                    style_cell={
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': 'none',
                        'padding': '2px 5px',
                        'fontSize': '12px'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{change} > 0',
                                'column_id': ['change', 'pct_change']
                            },
                            'color': BLOOMBERG_POSITIVE
                        },
                        {
                            'if': {
                                'filter_query': '{change} < 0',
                                'column_id': ['change', 'pct_change']
                            },
                            'color': BLOOMBERG_NEGATIVE
                        }
                    ]
                )
            ], style=PANEL_STYLE),
            
            # Strategy Performance (moved from center column)
            html.Div([
                html.Div("STRATEGY PERFORMANCE", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                dcc.Graph(id='pnl-graph', config={'displayModeBar': False})
            ], style=PANEL_STYLE),
            
            # Indices
            html.Div([
                html.Div("INDICES", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                dash_table.DataTable(
                    id='indices-table',
                    columns=[
                        {'name': 'Symbol', 'id': 'symbol'},
                        {'name': 'Price', 'id': 'price'},
                        {'name': 'Chg', 'id': 'change'},
                        {'name': '%Chg', 'id': 'pct_change'}
                    ],
                    style_header={
                        'backgroundColor': BLOOMBERG_BG,
                        'color': BLOOMBERG_TEXT,
                        'fontWeight': 'bold',
                        'border': 'none'
                    },
                    style_cell={
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': 'none',
                        'padding': '2px 5px',
                        'fontSize': '12px'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{change} > 0',
                                'column_id': ['change', 'pct_change']
                            },
                            'color': BLOOMBERG_POSITIVE
                        },
                        {
                            'if': {
                                'filter_query': '{change} < 0',
                                'column_id': ['change', 'pct_change']
                            },
                            'color': BLOOMBERG_NEGATIVE
                        }
                    ]
                )
            ], style=PANEL_STYLE),
            
            # Command terminal (moved from bottom)
            html.Div([
                html.Div("COMMAND TERMINAL", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                html.Div(id='terminal-output', style={
                    'backgroundColor': '#1a1a1a',
                    'color': BLOOMBERG_TEXT,
                    'height': '80px',
                    'overflowY': 'auto',
                    'border': f'1px solid {BLOOMBERG_BORDER}',
                    'padding': '5px',
                    'fontSize': '12px',
                    'fontFamily': 'Courier New, monospace',
                    'marginBottom': '5px'
                }),
                dcc.Input(
                    id='terminal-input',
                    type='text',
                    placeholder='Enter command (e.g., MSFT US EQUITY, HELP, NEWS)',
                    style={
                        'width': '100%',
                        'padding': '5px',
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': f'1px solid {BLOOMBERG_BORDER}',
                        'fontFamily': 'Courier New, monospace',
                        'fontSize': '12px'
                    },
                    n_submit=0
                )
            ], style=PANEL_STYLE)
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Center column - Charts
        html.Div([
            # Price charts - first row
            html.Div([
                html.Div([
                    dcc.Graph(id=f'{asset.lower()}-graph', config={'displayModeBar': False})
                ], style={'width': '32%', 'display': 'inline-block', **GRAPH_STYLE})
                for asset in CRYPTO_ASSETS[:3]
            ], style={'display': 'flex', 'justifyContent': 'space-between'}),
            
            # Price charts - second row
            html.Div([
                html.Div([
                    dcc.Graph(id=f'{asset.lower()}-graph', config={'displayModeBar': False})
                ], style={'width': '32%', 'display': 'inline-block', **GRAPH_STYLE})
                for asset in CRYPTO_ASSETS[3:]
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '5px'})
        ], style={'width': '50%', 'display': 'inline-block', 'marginLeft': '5px', 'marginRight': '5px'}),
        
        # Right column - News, positions, and stats
        html.Div([
            # News feed
            html.Div([
                html.Div("TOP NEWS", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                html.Div([
                    html.Div([
                        html.Span(f"{item['time']} ", style={'color': BLOOMBERG_HIGHLIGHT}),
                        html.Span(f"{item['headline']} ", style={'color': BLOOMBERG_TEXT}),
                        html.Span(f"({item['source']})", style={'color': '#666666'})
                    ], style={'marginBottom': '5px', 'fontSize': '12px'})
                    for item in NEWS_DATA
                ], style={'height': '200px', 'overflowY': 'auto'})
            ], style=PANEL_STYLE),
            
            # Orders/positions
            html.Div([
                html.Div("POSITIONS", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                dash_table.DataTable(
                    id='positions-table',
                    columns=[
                        {'name': 'Symbol', 'id': 'symbol'},
                        {'name': 'Qty', 'id': 'quantity'},
                        {'name': 'Avg Price', 'id': 'avg_price'},
                        {'name': 'Mkt Value', 'id': 'market_value'},
                        {'name': 'PnL', 'id': 'pnl'}
                    ],
                    style_header={
                        'backgroundColor': BLOOMBERG_BG,
                        'color': BLOOMBERG_TEXT,
                        'fontWeight': 'bold',
                        'border': 'none'
                    },
                    style_cell={
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': 'none',
                        'padding': '2px 5px',
                        'fontSize': '12px'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{pnl} > 0',
                                'column_id': 'pnl'
                            },
                            'color': BLOOMBERG_POSITIVE
                        },
                        {
                            'if': {
                                'filter_query': '{pnl} < 0',
                                'column_id': 'pnl'
                            },
                            'color': BLOOMBERG_NEGATIVE
                        }
                    ]
                )
            ], style=PANEL_STYLE),
            
            # Stats (moved from center column)
            html.Div([
                html.Div("STATS", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '5px'
                }),
                html.Div(id='stats-output', style={
                    'color': BLOOMBERG_TEXT,
                    'whiteSpace': 'pre-wrap',
                    'backgroundColor': '#1a1a1a',
                    'padding': '5px',
                    'border': f'1px solid {BLOOMBERG_BORDER}',
                    'height': '300px',
                    'overflowY': 'auto',
                    'fontSize': '12px',
                    'fontFamily': 'Courier New, monospace'
                })
            ], style=PANEL_STYLE)
        ], style={'width': '24%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'height': 'calc(100vh - 40px)'}),
    
    # Hidden div to trigger updates
    html.Div(id='hidden-div', style={'display': 'none'}),
    
    # Interval components
    dcc.Interval(id='datetime-interval', interval=1000, n_intervals=0),
    dcc.Interval(id='data-interval', interval=5000, n_intervals=0)
], style=STYLE)

# Callback to update date/time display
@app.callback(
    Output('datetime-display', 'children'),
    Input('datetime-interval', 'n_intervals')
)
def update_datetime(n):
    now = datetime.datetime.now()
    return now.strftime("%a %b %d %Y %H:%M:%S")

# Callback to update last update time
@app.callback(
    Output('last-update', 'children'),
    Input('data-interval', 'n_intervals')
)
def update_last_update(n):
    now = datetime.datetime.now()
    return f"LAST UPDATE: {now.strftime('%H:%M:%S')}"

# Main data update callback
@app.callback(
    [Output(f'{asset.lower()}-graph', 'figure') for asset in CRYPTO_ASSETS] +
    [Output('pnl-graph', 'figure'),
     Output('stats-output', 'children'),
     Output('crypto-table', 'data'),
     Output('commodities-table', 'data'),
     Output('indices-table', 'data'),
     Output('positions-table', 'data')],
    Input('data-interval', 'n_intervals')
)
def update_data(n):
    # Load individual price data files for each asset
    price_dfs = {}
    for asset in CRYPTO_ASSETS:
        try:
            with open(f'data/{asset.lower()}_prices.json', 'r') as f:
                asset_data = json.load(f)
                price_dfs[asset] = pd.DataFrame(asset_data)
        except FileNotFoundError:
            print(f"Warning: Price data for {asset} not found.")
            # Create empty DataFrame with timestamp column as fallback
            price_dfs[asset] = pd.DataFrame({"timestamp": [], f"{asset}": []})

    # Load PnL data
    try:
        with open('data/strategy_pnl.json', 'r') as f:
            pnl_data = json.load(f)
        pnl_df = pd.DataFrame(pnl_data)
    except FileNotFoundError:
        print("Warning: PnL data not found.")
        pnl_df = pd.DataFrame({"timestamp": [], "pnl": []})

    # Load stats data
    try:
        with open('data/strategy_stats.json', 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        print("Warning: Stats data not found.")
        stats = {"error": "Statistics data not available"}
        
    # Load market data (crypto, commodities, indices, positions)
    try:
        with open('data/crypto_market.json', 'r') as f:
            crypto_table_data = json.load(f)
    except FileNotFoundError:
        print("Warning: Crypto market data not found.")
        crypto_table_data = [
            {'symbol': asset, 'price': 0.0, 'change': 0.0, 'pct_change': 0.0, 'volume': '0K'} 
            for asset in CRYPTO_ASSETS
        ]
        
    try:
        with open('data/commodities_market.json', 'r') as f:
            commodities_table_data = json.load(f)
    except FileNotFoundError:
        print("Warning: Commodities market data not found.")
        commodities_table_data = [
            {'symbol': commodity, 'price': 0.0, 'change': 0.0, 'pct_change': 0.0} 
            for commodity in COMMODITIES
        ]
        
    try:
        with open('data/indices_market.json', 'r') as f:
            indices_table_data = json.load(f)
    except FileNotFoundError:
        print("Warning: Indices market data not found.")
        indices_table_data = [
            {'symbol': index, 'price': 0.0, 'change': 0.0, 'pct_change': 0.0} 
            for index in INDICES
        ]
        
    try:
        with open('data/positions.json', 'r') as f:
            positions_table_data = json.load(f)
    except FileNotFoundError:
        print("Warning: Positions data not found.")
        positions_table_data = []
    
    # Generate crypto price charts
    figures = []
    for asset in CRYPTO_ASSETS:
        df = price_dfs[asset]
        
        if not df.empty and 'timestamp' in df.columns and asset in df.columns:
            fig = {
                'data': [{
                    'x': df['timestamp'],
                    'y': df[asset],
                    'type': 'line',
                    'name': asset,
                    'line': {'color': BLOOMBERG_HIGHLIGHT}
                }],
                'layout': {
                    'plot_bgcolor': '#1a1a1a',
                    'paper_bgcolor': '#1a1a1a',
                    'font': {'color': BLOOMBERG_TEXT},
                    'margin': {'l': 30, 'r': 10, 't': 30, 'b': 30},
                    'title': f'{asset}/USD',
                    'titlefont': {'size': 12},
                    'xaxis': {'showgrid': False},
                    'yaxis': {'showgrid': True, 'gridcolor': BLOOMBERG_BORDER}
                }
            }
        else:
            # Empty chart if data not available
            fig = {
                'data': [],
                'layout': {
                    'plot_bgcolor': '#1a1a1a',
                    'paper_bgcolor': '#1a1a1a',
                    'font': {'color': BLOOMBERG_TEXT},
                    'margin': {'l': 30, 'r': 10, 't': 30, 'b': 30},
                    'title': f'{asset}/USD - No Data',
                    'titlefont': {'size': 12},
                    'xaxis': {'showgrid': False},
                    'yaxis': {'showgrid': True, 'gridcolor': BLOOMBERG_BORDER}
                }
            }
        figures.append(fig)

    # Generate PnL chart
    if not pnl_df.empty and 'timestamp' in pnl_df.columns and 'pnl' in pnl_df.columns:
        pnl_fig = {
            'data': [{
                'x': pnl_df['timestamp'],
                'y': pnl_df['pnl'],
                'type': 'line',
                'name': 'PnL',
                'line': {'color': BLOOMBERG_HIGHLIGHT}
            }],
            'layout': {
                'plot_bgcolor': '#1a1a1a',
                'paper_bgcolor': '#1a1a1a',
                'font': {'color': BLOOMBERG_TEXT},
                'margin': {'l': 30, 'r': 10, 't': 30, 'b': 30},
                'title': 'Strategy Performance',
                'titlefont': {'size': 12},
                'xaxis': {'showgrid': False},
                'yaxis': {'showgrid': True, 'gridcolor': BLOOMBERG_BORDER}
            }
        }
    else:
        pnl_fig = {
            'data': [],
            'layout': {
                'plot_bgcolor': '#1a1a1a',
                'paper_bgcolor': '#1a1a1a',
                'font': {'color': BLOOMBERG_TEXT},
                'margin': {'l': 30, 'r': 10, 't': 30, 'b': 30},
                'title': 'Strategy Performance - No Data',
                'titlefont': {'size': 12},
                'xaxis': {'showgrid': False},
                'yaxis': {'showgrid': True, 'gridcolor': BLOOMBERG_BORDER}
            }
        }

    # Format stats display
    stats_display = json.dumps(stats, indent=2)

    return figures + [pnl_fig, stats_display, crypto_table_data, commodities_table_data, indices_table_data, positions_table_data]

# Command terminal callback
@app.callback(
    Output('terminal-output', 'children'),
    Input('terminal-input', 'n_submit'),
    State('terminal-input', 'value'),
    State('terminal-output', 'children'),
    prevent_initial_call=True
)
def update_terminal(n_submit, command, history):
    if not command:
        return history
    
    # Process command (simple example)
    if command.lower() == 'help':
        response = "Available commands: HELP, NEWS, POSITIONS, [TICKER] (e.g. BTC US CRYPTO)"
    elif command.lower() == 'news':
        response = "Latest news headlines displayed above"
    elif command.lower() == 'positions':
        response = "Current positions displayed above"
    else:
        response = f"Command '{command}' not recognized. Type HELP for available commands."
    
    new_entry = f"> {command}\n{response}"
    updated = f"{history}\n{new_entry}" if history else new_entry
    
    # Clear input
    return updated

if __name__ == '__main__':
    app.run(debug=False)