import json
import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import datetime

import time
import os
import requests

# Replace with your NewsAPI key
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

app = Dash(__name__)
app.title = "TradeByte Terminal - Bloomberg Style"

CRYPTO_ASSETS = ['BTC', 'ETH', 'SOL', 'LTC', 'XRP', 'ADA']
COMMODITIES = ['Gold', 'Silver', 'Oil', 'NatGas']
INDICES = ['SPX', 'NDX', 'DJI', 'RUT']

# Bloomberg Terminal color scheme
BLOOMBERG_BG = '#0f0f0f'  # Dark background
BLOOMBERG_TEXT = '#ff8c00'  # Bloomberg orange/amber
BLOOMBERG_HIGHLIGHT = '#ffcc00'  # Brighter highlight
BLOOMBERG_BORDER = '#333333'  # Dark borders
BLOOMBERG_POSITIVE = '#00ff00'  # Green for positive
BLOOMBERG_NEGATIVE = '#ff0000'  # Red for negative

# CSS styling for Bloomberg-style appearance
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

# Sample news data
timestamp = time.time()
formatted_time = time.strftime("%I:%M %p", time.localtime(timestamp))
NEWS_DATA = [{"time": formatted_time, "headline": headline.split(' - ')[0], "source": headline.split(' - ')[1] if ' - ' in headline else ""} for headline in fetch_headlines()]

app.layout = html.Div([
    # Header with status bar
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
    # Load data from files (in a real app, this would be from APIs)
    with open('data/prices.json', 'r') as f:
        price_data = json.load(f)
    price_df = pd.DataFrame(price_data)

    with open('data/pnl.json', 'r') as f:
        pnl_data = json.load(f)
    pnl_df = pd.DataFrame(pnl_data)

    with open('data/stats.json', 'r') as f:
        stats = json.load(f)
    
    # Generate crypto price charts
    figures = []
    for asset in CRYPTO_ASSETS:
        fig = {
            'data': [{
                'x': price_df['timestamp'],
                'y': price_df[asset],
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
        figures.append(fig)

    # Generate PnL chart
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

    # Format stats display
    stats_display = json.dumps(stats, indent=2)
    
    # Generate table data (mock data for demo)
    crypto_table_data = [
        {'symbol': 'BTC', 'price': 65432.10, 'change': 1234.56, 'pct_change': 1.92, 'volume': '25.3K'},
        {'symbol': 'ETH', 'price': 3456.78, 'change': -23.45, 'pct_change': -0.67, 'volume': '18.7K'},
        {'symbol': 'SOL', 'price': 123.45, 'change': 5.67, 'pct_change': 4.82, 'volume': '9.2K'},
        {'symbol': 'LTC', 'price': 78.90, 'change': -1.23, 'pct_change': -1.54, 'volume': '5.6K'},
        {'symbol': 'XRP', 'price': 0.5678, 'change': 0.0123, 'pct_change': 2.21, 'volume': '42.1K'},
        {'symbol': 'ADA', 'price': 0.4567, 'change': -0.0056, 'pct_change': -1.21, 'volume': '35.8K'}
    ]
    
    commodities_table_data = [
        {'symbol': 'Gold', 'price': 1987.50, 'change': 12.30, 'pct_change': 0.62},
        {'symbol': 'Silver', 'price': 23.45, 'change': -0.12, 'pct_change': -0.51},
        {'symbol': 'Oil', 'price': 78.90, 'change': 1.23, 'pct_change': 1.58},
        {'symbol': 'NatGas', 'price': 2.345, 'change': -0.056, 'pct_change': -2.33}
    ]
    
    indices_table_data = [
        {'symbol': 'SPX', 'price': 5123.45, 'change': 23.45, 'pct_change': 0.46},
        {'symbol': 'NDX', 'price': 17890.12, 'change': 123.45, 'pct_change': 0.69},
        {'symbol': 'DJI', 'price': 38765.43, 'change': -123.45, 'pct_change': -0.32},
        {'symbol': 'RUT', 'price': 2012.34, 'change': 5.67, 'pct_change': 0.28}
    ]
    
    positions_table_data = [
        {'symbol': 'BTC', 'quantity': 1.5, 'avg_price': 58210.00, 'market_value': 98148.15, 'pnl': 39938.15},
        {'symbol': 'ETH', 'quantity': 10, 'avg_price': 3200.00, 'market_value': 34567.80, 'pnl': 2567.80},
        {'symbol': 'SOL', 'quantity': 50, 'avg_price': 110.00, 'market_value': 6172.50, 'pnl': 1172.50},
        {'symbol': 'Gold', 'quantity': 5, 'avg_price': 1950.00, 'market_value': 9937.50, 'pnl': 37.50}
    ]

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