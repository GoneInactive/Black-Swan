# src/utils/plotter.py

from dearpygui.core import *
from dearpygui.simple import *

def plot_price(df, symbol="Crypto"):
    """
    Launches an interactive window to plot OHLC price data with DearPyGUI.
    Assumes df has columns: ['timestamp', 'open', 'high', 'low', 'close']
    """
    if df is None or df.empty:
        print("[!] No data to plot.")
        return

    # Convert timestamp to string (DearPyGUI doesn't like datetime)
    df['timestamp'] = df['timestamp'].astype(str)

    # Extract data
    x = df['timestamp'].tolist()
    y_close = df['close'].tolist()
    y_open = df['open'].tolist()
    y_high = df['high'].tolist()
    y_low = df['low'].tolist()

    with window(f"{symbol} Price Chart"):
        add_plot("Price Plot", height=400)
        add_line_series("Price Plot", "Close", x, y_close)
        add_line_series("Price Plot", "Open", x, y_open)
        add_line_series("Price Plot", "High", x, y_high)
        add_line_series("Price Plot", "Low", x, y_low)
        add_plot_legend("Price Plot", location=1, horizontal=True)
        add_text(f"Last Close: {y_close[-1]:.2f}")
        add_button("Close Window", callback=lambda: delete_item(f"{symbol} Price Chart"))

    start_dearpygui()

'''
Test usage in main.py:
from utils.plotter import plot_price
from helpers import prepare_data

df = kraken.get_ohlc(pair='XXBTZUSD', interval=60)
df = prepare_data(df)

plot_price(df, symbol="BTC/USD")
'''

