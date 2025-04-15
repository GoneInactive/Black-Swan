# utils/account_tools.py

import krakenex
from pykrakenapi import KrakenAPI
from src.config_loader import KRAKEN_API_KEY, KRAKEN_API_SECRET

# Initialize Kraken API with keys from config
api = krakenex.API(key=KRAKEN_API_KEY, secret=KRAKEN_API_SECRET)
k = KrakenAPI(api)

def get_account_balance():
    try:
        return k.get_account_balance()
    except Exception as e:
        print(f"[Error] Fetching account balance: {e}")
        return None

def get_open_orders():
    try:
        return api.query_private('OpenOrders')['result']['open']
    except Exception as e:
        print(f"[Error] Fetching open orders: {e}")
        return None

def get_closed_orders():
    try:
        return api.query_private('ClosedOrders')['result']['closed']
    except Exception as e:
        print(f"[Error] Fetching closed orders: {e}")
        return None

def get_recent_trades():
    try:
        return api.query_private('TradesHistory')['result']['trades']
    except Exception as e:
        print(f"[Error] Fetching recent trades: {e}")
        return None

def get_trade_volume():
    try:
        return api.query_private('TradeVolume')['result']
    except Exception as e:
        print(f"[Error] Fetching trade volume: {e}")
        return None
