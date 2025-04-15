# src/helpers.py

import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def format_timestamp(timestamp):
    """
    Converts a Kraken timestamp to a datetime object.
    """
    return datetime.utcfromtimestamp(timestamp)

def prepare_data(df):
    """
    Prepares the data for backtesting or live trading.
    - Renames columns to lowercase
    - Converts timestamp to datetime
    """
    df = df.rename(columns=str.lower)
    df['timestamp'] = df['timestamp'].apply(format_timestamp)
    return df

def save_data(df, filename):
    """
    Saves a DataFrame to CSV.
    """
    df.to_csv(filename, index=False)
    logger.info(f"Data saved to {filename}")

def load_data(filename):
    """
    Loads a CSV into a DataFrame.
    """
    try:
        df = pd.read_csv(filename)
        logger.info(f"Data loaded from {filename}")
        return df
    except Exception as e:
        logger.error(f"Error loading data from {filename}: {e}")
        return None

def compute_trade_size(balance, price, order_size):
    """
    Calculate the size of the trade based on balance, asset price, and desired order size percentage.
    """
    return (balance * order_size) / price

def log_trade(action, price, size):
    """
    Log trade details.
    """
    logger.info(f"Executed {action} trade - Price: ${price:.2f}, Size: {size} units")

def is_trade_allowed(balance, price, order_size, slippage=0.01):
    """
    Check if a trade is allowed based on balance, price, order size, and slippage tolerance.
    """
    trade_size = compute_trade_size(balance, price, order_size)
    if trade_size > 0 and balance >= trade_size * price * (1 + slippage):
        return True
    return False
