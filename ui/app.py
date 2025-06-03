import json
import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import datetime
import time
import os
import requests
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "clients")))

from kraken_python_client import KrakenPythonClient

def ensure_data_directory():
    """Create data directory if it doesn't exist and create placeholder files if needed"""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created data directory")
        
        placeholder_files = {
            'news.json': [
                {"time": "10:23 AM", "headline": "Welcome to TradeByte Terminal", "source": "System"}
            ]
        }
        
        for filename, data in placeholder_files.items():
            with open(f'data/{filename}', 'w') as f:
                json.dump(data, f)

app = Dash(__name__)
app.title = "TradeByte Terminal"

CRYPTO_ASSETS = ['BTC', 'ETHZUSD', 'SOLZUSD', 'LTCZUSD', 'XRPZUSD', 'EURZUSD']
ensure_data_directory()

# Initialize Kraken client
kraken_client = KrakenPythonClient()

API_KEY = '3659930e56ec414a958d717950a981ff'
URL = 'https://newsapi.org/v2/top-headlines'

def fetch_headlines():
    params = {
        'country': 'us',
        'category': 'business',
        'apiKey': API_KEY
    }
    try:
        response = requests.get(URL, params=params)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            headlines = []
            for article in articles:
                title = article.get('title', '')
                source = article.get('source', {}).get('name', 'Unknown')
                # Truncate long headlines
                if len(title) > 80:
                    title = title[:77] + '...'
                headlines.append(f"{title} - {source}")
            return headlines
        else:
            print(f"Failed to fetch news. Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"News API error: {e}")
        return []

def load_news_data():
    """Load news data from local JSON file instead of API"""
    try:
        timestamp = time.time()
        formatted_time = time.strftime("%I:%M %p", time.localtime(timestamp))
        news_items = []
        for headline in fetch_headlines():
            parts = headline.split(' - ', 1)
            if len(parts) == 2:
                news_items.append({
                    "time": formatted_time,
                    "headline": parts[0],
                    "source": parts[1]
                })
            else:
                news_items.append({
                    "time": formatted_time,
                    "headline": headline,
                    "source": "Unknown"
                })
        return news_items[:6]  # Return max 6 news items
    except Exception as e:
        print(f"Error loading news: {e}")
        return [{"time": formatted_time, "headline": "Error loading news", "source": "System"}]

NEWS_DATA = load_news_data()

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
    'padding': '0px',
    'margin': '-8px',
    'height': '100vh',
    'overflow': 'hidden'
}

PANEL_STYLE = {
    'backgroundColor': '#1a1a1a',
    'padding': '10px',
    'border': f'1px solid {BLOOMBERG_BORDER}',
    'margin': '5px',
    'borderRadius': '0px'
}

GRAPH_STYLE = {
    'backgroundColor': '#1a1a1a',
    'padding': '5px',
    'border': f'1px solid {BLOOMBERG_BORDER}',
    'margin': '5px',
    'borderRadius': '0px',
    'height': '200px'  # Fixed height for graphs
}

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
            'marginRight': '20px',
            'fontSize': '14px'
        }),
        html.Div("LIVE", style={
            'color': BLOOMBERG_POSITIVE,
            'display': 'inline-block',
            'marginRight': '20px',
            'fontWeight': 'bold',
            'fontSize': '14px'
        }),
        html.Div("CONNECTED", style={
            'color': BLOOMBERG_POSITIVE,
            'display': 'inline-block',
            'marginRight': '20px',
            'fontSize': '14px'
        }),
        html.Div(id='last-update', style={
            'display': 'inline-block',
            'marginRight': '20px',
            'fontSize': '14px'
        }),
    ], style={
        'borderBottom': f'1px solid {BLOOMBERG_BORDER}',
        'padding': '10px 5px',
        'marginBottom': '5px',
        'paddingLeft': '5px'
    }),
    
    # Main content area
    html.Div([
        # Left column - Market data and Mini charts
        html.Div([
            # Crypto prices
            html.Div([
                html.Div("CRYPTO PRICES", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'fontSize': '14px'
                }),
                dash_table.DataTable(
                    id='crypto-table',
                    columns=[
                        {'name': 'Symbol', 'id': 'symbol'},
                        {'name': 'Bid', 'id': 'bid'},
                        {'name': 'Ask', 'id': 'ask'},
                        {'name': 'Spread', 'id': 'spread'},
                        {'name': '% Spread', 'id': 'pct_spread'}
                    ],
                    style_header={
                        'backgroundColor': BLOOMBERG_BG,
                        'color': BLOOMBERG_TEXT,
                        'fontWeight': 'bold',
                        'border': 'none',
                        'fontSize': '12px'
                    },
                    style_cell={
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': 'none',
                        'padding': '5px',
                        'fontSize': '12px'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'column_id': ['bid', 'ask', 'spread', 'pct_spread']
                            },
                            'textAlign': 'right'
                        }
                    ],
                    style_table={'minWidth': '100%'},
                )
            ], style=PANEL_STYLE),
            
            # Price lookup module
            html.Div([
                html.Div("PRICE LOOKUP", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'fontSize': '14px'
                }),
                dcc.Input(
                    id='price-lookup-input',
                    type='text',
                    placeholder='Enter asset (e.g. BTC, ETH)',
                    style={
                        'width': '100%',
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': f'1px solid {BLOOMBERG_BORDER}',
                        'marginBottom': '10px',
                        'padding': '8px',
                        'fontSize': '12px'
                    }
                ),
                html.Div(id='price-lookup-output', style={
                    'backgroundColor': '#1a1a1a',
                    'color': BLOOMBERG_TEXT,
                    'padding': '10px',
                    'border': f'1px solid {BLOOMBERG_BORDER}',
                    'fontFamily': 'Courier New, monospace',
                    'fontSize': '12px',
                    'minHeight': '80px'
                })
            ], style=PANEL_STYLE),
            
            # Trader feature
            html.Div([
                html.Div("TRADE EXECUTION", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'fontSize': '14px'
                }),
                dcc.Input(
                    id='trade-asset-input',
                    type='text',
                    placeholder='Asset (e.g. BTC)',
                    style={
                        'width': '100%',
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': f'1px solid {BLOOMBERG_BORDER}',
                        'marginBottom': '10px',
                        'padding': '8px',
                        'fontSize': '12px'
                    }
                ),
                dcc.Input(
                    id='trade-price-input',
                    type='number',
                    placeholder='Price',
                    style={
                        'width': '100%',
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': f'1px solid {BLOOMBERG_BORDER}',
                        'marginBottom': '10px',
                        'padding': '8px',
                        'fontSize': '12px'
                    }
                ),
                dcc.Input(
                    id='trade-amount-input',
                    type='number',
                    placeholder='Amount',
                    style={
                        'width': '100%',
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': f'1px solid {BLOOMBERG_BORDER}',
                        'marginBottom': '10px',
                        'padding': '8px',
                        'fontSize': '12px'
                    }
                ),
                html.Div([
                    html.Button(
                        'BUY',
                        id='trade-buy-button',
                        style={
                            'width': '48%',
                            'backgroundColor': BLOOMBERG_POSITIVE,
                            'color': 'black',
                            'border': 'none',
                            'padding': '10px',
                            'fontWeight': 'bold',
                            'marginRight': '4%',
                            'cursor': 'pointer'
                        }
                    ),
                    html.Button(
                        'SELL',
                        id='trade-sell-button',
                        style={
                            'width': '48%',
                            'backgroundColor': BLOOMBERG_NEGATIVE,
                            'color': 'black',
                            'border': 'none',
                            'padding': '10px',
                            'fontWeight': 'bold',
                            'cursor': 'pointer'
                        }
                    )
                ], style={'display': 'flex', 'justifyContent': 'space-between'}),
                html.Div(id='trade-status', style={
                    'marginTop': '10px',
                    'fontSize': '12px',
                    'color': BLOOMBERG_HIGHLIGHT,
                    'minHeight': '20px'
                })
            ], style=PANEL_STYLE),
            
            # Command terminal
            html.Div([
                html.Div("COMMAND TERMINAL", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'fontSize': '14px'
                }),
                html.Div(id='terminal-output', style={
                    'backgroundColor': '#1a1a1a',
                    'color': BLOOMBERG_TEXT,
                    'height': '120px',
                    'overflowY': 'auto',
                    'border': f'1px solid {BLOOMBERG_BORDER}',
                    'padding': '10px',
                    'fontSize': '12px',
                    'fontFamily': 'Courier New, monospace',
                    'marginBottom': '10px',
                    'whiteSpace': 'pre-wrap'
                }),
                dcc.Input(
                    id='terminal-input',
                    type='text',
                    placeholder='Enter command (e.g., BUY BTC 0.1, SELL ETH 1, BALANCE, HELP)',
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': f'1px solid {BLOOMBERG_BORDER}',
                        'fontFamily': 'Courier New, monospace',
                        'fontSize': '12px'
                    },
                    n_submit=0
                )
            ], style=PANEL_STYLE)
        ], style={
            'width': '24%', 
            'display': 'inline-block', 
            'verticalAlign': 'top',
            'height': 'calc(100vh - 70px)',
            'overflowY': 'auto'
        }),
        
        # Center column - 3x2 grid of live pricing graphs
        html.Div([
            # Asset selection for each chart
            html.Div([
                html.Div([
                    dcc.Input(
                        id=f'chart-asset-{i}',
                        type='text',
                        placeholder='Asset (e.g. BTC)',
                        value=CRYPTO_ASSETS[i-1] if i-1 < len(CRYPTO_ASSETS) else '',
                        style={
                            'width': '90%',
                            'backgroundColor': '#1a1a1a',
                            'color': BLOOMBERG_TEXT,
                            'border': f'1px solid {BLOOMBERG_BORDER}',
                            'marginBottom': '5px',
                            'padding': '5px',
                            'fontSize': '12px'
                        }
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '1%'})
                for i in range(1, 7)
            ], style={'marginBottom': '10px'}),
            
            # Row 1
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='chart-1',
                        config={'displayModeBar': False},
                        style={'height': '100%'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', **GRAPH_STYLE, 'height': 'calc(33vh - 30px)'}),
                html.Div([
                    dcc.Graph(
                        id='chart-2',
                        config={'displayModeBar': False},
                        style={'height': '100%'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%', **GRAPH_STYLE, 'height': 'calc(33vh - 30px)'}),
                html.Div([
                    dcc.Graph(
                        id='chart-3',
                        config={'displayModeBar': False},
                        style={'height': '100%'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%', **GRAPH_STYLE, 'height': 'calc(33vh - 30px)'}),
            ], style={'marginBottom': '10px'}),
            
            # Row 2
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='chart-4',
                        config={'displayModeBar': False},
                        style={'height': '100%'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', **GRAPH_STYLE, 'height': 'calc(33vh - 30px)'}),
                html.Div([
                    dcc.Graph(
                        id='chart-5',
                        config={'displayModeBar': False},
                        style={'height': '100%'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%', **GRAPH_STYLE, 'height': 'calc(33vh - 30px)'}),
                html.Div([
                    dcc.Graph(
                        id='chart-6',
                        config={'displayModeBar': False},
                        style={'height': '100%'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%', **GRAPH_STYLE, 'height': 'calc(33vh - 30px)'}),
            ])
        ], style={
            'width': '50%', 
            'display': 'inline-block', 
            'marginLeft': '5px', 
            'marginRight': '5px',
            'height': 'calc(100vh - 70px)',
            'overflowY': 'auto'
        }),
        
        # Right column - News, positions, and stats
        html.Div([
            # News feed
            html.Div([
                html.Div("TOP NEWS", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'fontSize': '14px'
                }),
                html.Div([
                    html.Div([
                        html.Span(f"{item['time']} ", style={'color': BLOOMBERG_HIGHLIGHT, 'fontSize': '11px'}),
                        html.Span(f"{item['headline']} ", style={'color': BLOOMBERG_TEXT, 'fontSize': '11px'}),
                        html.Span(f"({item['source']})", style={'color': '#666666', 'fontSize': '10px'})
                    ], style={
                        'marginBottom': '10px', 
                        'paddingBottom': '5px', 
                        'borderBottom': f'1px solid {BLOOMBERG_BORDER}'
                    })
                    for item in NEWS_DATA
                ], style={
                    'height': '200px', 
                    'overflowY': 'auto',
                    'paddingRight': '5px'
                })
            ], style=PANEL_STYLE),
            
            # Balance/positions
            html.Div([
                html.Div("BALANCES", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'fontSize': '14px'
                }),
                dash_table.DataTable(
                    id='balance-table',
                    columns=[
                        {'name': 'Asset', 'id': 'asset'},
                        {'name': 'Balance', 'id': 'balance'}
                    ],
                    style_header={
                        'backgroundColor': BLOOMBERG_BG,
                        'color': BLOOMBERG_TEXT,
                        'fontWeight': 'bold',
                        'border': 'none',
                        'fontSize': '12px'
                    },
                    style_cell={
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': 'none',
                        'padding': '5px',
                        'fontSize': '12px'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'column_id': 'balance'
                            },
                            'textAlign': 'right'
                        }
                    ],
                    style_table={'minWidth': '100%'},
                )
            ], style=PANEL_STYLE),
            
            # Orders
            html.Div([
                html.Div("ORDERS", style={
                    'color': BLOOMBERG_HIGHLIGHT,
                    'fontWeight': 'bold',
                    'marginBottom': '10px',
                    'fontSize': '14px'
                }),
                dash_table.DataTable(
                    id='orders-table',
                    columns=[
                        {'name': 'Pair', 'id': 'pair'},
                        {'name': 'Type', 'id': 'type'},
                        {'name': 'Price', 'id': 'price'},
                        {'name': 'Amount', 'id': 'amount'},
                        {'name': 'Value', 'id': 'value'}
                    ],
                    style_header={
                        'backgroundColor': BLOOMBERG_BG,
                        'color': BLOOMBERG_TEXT,
                        'fontWeight': 'bold',
                        'border': 'none',
                        'fontSize': '12px'
                    },
                    style_cell={
                        'backgroundColor': '#1a1a1a',
                        'color': BLOOMBERG_TEXT,
                        'border': 'none',
                        'padding': '5px',
                        'fontSize': '12px'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'column_id': ['price', 'amount', 'value']
                            },
                            'textAlign': 'right'
                        },
                        {
                            'if': {
                                'filter_query': '{type} = buy',
                                'column_id': 'type'
                            },
                            'color': BLOOMBERG_POSITIVE
                        },
                        {
                            'if': {
                                'filter_query': '{type} = sell',
                                'column_id': 'type'
                            },
                            'color': BLOOMBERG_NEGATIVE
                        }
                    ],
                    style_table={'minWidth': '100%'},
                )
            ], style=PANEL_STYLE)
        ], style={
            'width': '24%', 
            'display': 'inline-block', 
            'verticalAlign': 'top',
            'height': 'calc(100vh - 70px)',
            'overflowY': 'auto'
        })
    ], style={
        'display': 'flex', 
        'height': 'calc(100vh - 60px)',
        'paddingLeft': '5px',
        'paddingRight': '5px'
    }),
    
    # Hidden div to trigger updates
    html.Div(id='hidden-div', style={'display': 'none'}),
    
    # Interval components
    dcc.Interval(id='datetime-interval', interval=1000, n_intervals=0),
    dcc.Interval(id='data-interval', interval=5000, n_intervals=0),
    
    # Store for chart data
    dcc.Store(id='chart-data-store')
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

# Callback to update crypto prices with real data
@app.callback(
    Output('crypto-table', 'data'),
    Input('data-interval', 'n_intervals')
)
def update_crypto_prices(n):
    crypto_data = []
    for asset in CRYPTO_ASSETS:
        try:
            pair = f"X{asset}" if asset != 'BTC' else "XXBTZUSD"
            bid = float(kraken_client.get_bid(pair))
            ask = float(kraken_client.get_ask(pair))
            spread = ask - bid
            pct_spread = (spread / bid) * 100
            
            crypto_data.append({
                'symbol': asset,
                'bid': f"{bid:.2f}",
                'ask': f"{ask:.2f}",
                'spread': f"{spread:.2f}",
                'pct_spread': f"{pct_spread:.2f}%"
            })
        except Exception as e:
            print(f"Error getting price for {asset}: {e}")
            crypto_data.append({
                'symbol': asset,
                'bid': "N/A",
                'ask': "N/A",
                'spread': "N/A",
                'pct_spread': "N/A"
            })
    
    return crypto_data

# Callback to update balance table
@app.callback(
    Output('balance-table', 'data'),
    Input('data-interval', 'n_intervals')
)
def update_balance(n):
    try:
        balance = kraken_client.get_balance()
        if balance is None:
            return []
            
        balance_data = []
        for asset, amount in balance.items():
            try:
                # Filter out assets with zero balance
                if float(amount) > 0:
                    balance_data.append({
                        'asset': asset,
                        'balance': f"{float(amount):.6f}"
                    })
            except (ValueError, TypeError):
                continue
                
        return balance_data
    except Exception as e:
        print(f"Error getting balance: {e}")
        return []

# Callback to update orders table
@app.callback(
    Output('orders-table', 'data'),
    Input('data-interval', 'n_intervals')
)
def update_orders(n):
    try:
        orders_df = kraken_client.get_open_orders()
        if orders_df is None or orders_df.empty:
            return []
            
        orders_data = []
        for _, row in orders_df.iterrows():
            try:
                # Extract pair and simplify
                pair = row.get('descr', {}).get('pair', '')
                if pair.startswith('X') and pair.endswith('ZUSD'):
                    pair = pair[1:-4]
                
                # Get order type
                order_type = row.get('descr', {}).get('type', '').split()[0].lower()
                
                # Calculate value
                vol = float(row.get('vol', 0))
                price = float(row.get('price', 0))
                value = vol * price
                
                orders_data.append({
                    'pair': pair,
                    'type': order_type,
                    'price': f"{price:.2f}",
                    'amount': f"{vol:.6f}",
                    'value': f"{value:.2f}"
                })
            except (KeyError, TypeError, ValueError):
                continue
                
        return orders_data
        
    except Exception as e:
        print(f"Error getting orders: {e}")
        return []

# Callback to update the 6 charts in the grid
@app.callback(
    [Output(f'chart-{i}', 'figure') for i in range(1, 7)],
    [Input(f'chart-asset-{i}', 'value') for i in range(1, 7)],
    Input('data-interval', 'n_intervals')
)
def update_grid_charts(*args):
    # Split inputs into assets and n_intervals
    assets = args[:6]
    n_intervals = args[6]
    
    figures = []
    
    for i, asset in enumerate(assets, 1):
        if not asset:
            # Empty figure if no asset specified
            fig = {
                'data': [],
                'layout': {
                    'plot_bgcolor': '#1a1a1a',
                    'paper_bgcolor': '#1a1a1a',
                    'font': {'color': BLOOMBERG_TEXT, 'size': 10},
                    'margin': {'l': 30, 'r': 10, 't': 30, 'b': 30},
                    'title': f'Chart {i} - Enter Asset',
                    'xaxis': {'showgrid': False},
                    'yaxis': {'showgrid': True, 'gridcolor': BLOOMBERG_BORDER}
                }
            }
            figures.append(fig)
            continue
            
        try:
            asset = asset.upper()
            pair = f"X{asset}" if asset != 'BTC' else "XXBTZUSD"
            bid = float(kraken_client.get_bid(pair))
            ask = float(kraken_client.get_ask(pair))
            mid = (bid + ask) / 2
            
            fig = {
                'data': [
                    {
                        'x': [0, 1],
                        'y': [bid, bid],
                        'type': 'line',
                        'name': 'Bid',
                        'line': {'color': BLOOMBERG_POSITIVE, 'width': 2}
                    },
                    {
                        'x': [0, 1],
                        'y': [ask, ask],
                        'type': 'line',
                        'name': 'Ask',
                        'line': {'color': BLOOMBERG_NEGATIVE, 'width': 2}
                    },
                    {
                        'x': [0, 1],
                        'y': [mid, mid],
                        'type': 'line',
                        'name': 'Mid',
                        'line': {'color': BLOOMBERG_HIGHLIGHT, 'width': 1, 'dash': 'dot'}
                    }
                ],
                'layout': {
                    'plot_bgcolor': '#1a1a1a',
                    'paper_bgcolor': '#1a1a1a',
                    'font': {'color': BLOOMBERG_TEXT, 'size': 10},
                    'margin': {'l': 30, 'r': 10, 't': 30, 'b': 30},
                    'title': f'{asset}',
                    'showlegend': False,
                    'xaxis': {'showgrid': False, 'showticklabels': False},
                    'yaxis': {'showgrid': True, 'gridcolor': BLOOMBERG_BORDER}
                }
            }
        except Exception as e:
            print(f"Error creating chart for {asset}: {e}")
            fig = {
                'data': [],
                'layout': {
                    'plot_bgcolor': '#1a1a1a',
                    'paper_bgcolor': '#1a1a1a',
                    'font': {'color': BLOOMBERG_TEXT, 'size': 10},
                    'margin': {'l': 30, 'r': 10, 't': 30, 'b': 30},
                    'title': f'{asset} - Error',
                    'xaxis': {'showgrid': False},
                    'yaxis': {'showgrid': True, 'gridcolor': BLOOMBERG_BORDER}
                }
            }
        figures.append(fig)
    
    return figures

# Add new callbacks for the price lookup and trader features
@app.callback(
    Output('price-lookup-output', 'children'),
    Input('price-lookup-input', 'value'),
    Input('data-interval', 'n_intervals')
)
def update_price_lookup(asset, n):
    if not asset:
        return "Enter an asset symbol to lookup prices"
    
    try:
        asset = asset.upper()
        pair = f"X{asset}" if asset != 'BTC' else "XXBTZUSD"
        bid = float(kraken_client.get_bid(pair))
        ask = float(kraken_client.get_ask(pair))
        mid = (bid + ask) / 2
        spread = ask - bid
        pct_spread = (spread / bid) * 100
        
        return f"""Bid: {bid:.2f}
Ask: {ask:.2f}
Mid: {mid:.2f}
Spread: {spread:.2f} ({pct_spread:.2f}%)"""
    except Exception as e:
        return f"Error: Could not get prices for {asset}"

@app.callback(
    Output('trade-status', 'children'),
    Output('terminal-output', 'children', allow_duplicate=True),
    Input('trade-buy-button', 'n_clicks'),
    Input('trade-sell-button', 'n_clicks'),
    State('trade-asset-input', 'value'),
    State('trade-price-input', 'value'),
    State('trade-amount-input', 'value'),
    State('terminal-output', 'children'),
    prevent_initial_call=True
)
def execute_trade(buy_clicks, sell_clicks, asset, price, amount, terminal_history):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "", terminal_history
    
    if not all([asset, price, amount]):
        return "Error: Please fill all fields", terminal_history
    
    try:
        asset = asset.upper()
        pair = f"X{asset}" if asset != 'BTC' else "XXBTZUSD"
        side = 'buy' if 'trade-buy-button' in ctx.triggered[0]['prop_id'] else 'sell'
        
        # Place order
        response = kraken_client.add_order(
            asset=pair,
            side=side,
            price=str(price),
            volume=str(amount)
        )
        
        status = f"{side.upper()} order placed for {amount} {asset} at {price}"
        
        # Update terminal
        new_entry = f"> {side} {asset} {amount} @ {price}\n{status}"
        updated_terminal = f"{terminal_history}\n{new_entry}" if terminal_history else new_entry
        
        return status, updated_terminal
    except Exception as e:
        return f"Error: {str(e)}", terminal_history

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
    
    # Process trading commands
    try:
        if command.lower().startswith('buy '):
            parts = command.split()
            if len(parts) >= 3:
                asset = parts[1].upper()
                amount = float(parts[2])
                pair = f"X{asset}" if asset != 'BTC' else "XXBTZUSD"
                price = float(kraken_client.get_ask(pair))
                
                # Place order
                response = kraken_client.add_order(
                    asset=pair,
                    side='buy',
                    price=str(price),
                    volume=str(amount)
                )
                response = f"BUY order placed for {amount} {asset} at {price:.2f}"
                
        elif command.lower().startswith('sell '):
            parts = command.split()
            if len(parts) >= 3:
                asset = parts[1].upper()
                amount = float(parts[2])
                pair = f"X{asset}" if asset != 'BTC' else "XXBTZUSD"
                price = float(kraken_client.get_bid(pair))
                
                # Place order
                response = kraken_client.add_order(
                    asset=pair,
                    side='sell',
                    price=str(price),
                    volume=str(amount)
                )
                response = f"SELL order placed for {amount} {asset} at {price:.2f}"
                
        elif command.lower() == 'cancel all':
            orders_df = kraken_client.get_open_orders()
            if not orders_df.empty:
                for order_id in orders_df['order_id']:
                    kraken_client.cancel_order(order_id)
                response = "All orders cancelled"
            else:
                response = "No open orders to cancel"
                
        elif command.lower() == 'balance':
            balance = kraken_client.get_balance()
            response = "\n".join([f"{asset}: {float(amount):.6f}" for asset, amount in balance.items() if float(amount) > 0])
            
        elif command.lower() == 'orders':
            orders_df = kraken_client.get_open_orders()
            if orders_df.empty:
                response = "No open orders"
            else:
                response = "Open orders:\n" + "\n".join([
                    f"{row['descr_pair']} {row['descr_type']} {row['vol']} @ {row['descr_price']}"
                    for _, row in orders_df.iterrows()
                ])
                
        elif command.lower() == 'help':
            response = """Available commands:
- BUY [ASSET] [AMOUNT] - Place buy order
- SELL [ASSET] [AMOUNT] - Place sell order
- CANCEL ALL - Cancel all open orders
- BALANCE - Show account balance
- ORDERS - List open orders
- HELP - Show this help"""
        else:
            response = f"Command '{command}' not recognized. Type HELP for available commands."
            
    except Exception as e:
        response = f"Error: {str(e)}"
    
    new_entry = f"> {command}\n{response}"
    updated = f"{history}\n{new_entry}" if history else new_entry
    
    return updated

if __name__ == '__main__':
    app.run(debug=False)