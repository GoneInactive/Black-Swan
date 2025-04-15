# src/kraken_api.py

import krakenex
import time
from pykrakenapi import KrakenAPI

class KrakenClient:
    def __init__(self, api_key, api_secret):
        self.k = krakenex.API()
        self.k.key = api_key
        self.k.secret = api_secret
        self.kraken = KrakenAPI(self.k)

    def get_balance(self):
        try:
            return self.kraken.get_account_balance()
        except Exception as e:
            print(f"[!] Error fetching balance: {e}")
            return None

    def get_ohlc(self, pair='XXBTZUSD', interval=60):
        """Get OHLC data. Interval is in minutes."""
        try:
            df, _ = self.kraken.get_ohlc_data(pair, interval=interval)
            df = df.rename(columns=str.lower)
            return df
        except Exception as e:
            print(f"[!] Error fetching OHLC data: {e}")
            return None

    def place_order(self, pair, side, order_type='market', volume=0.001):
        """
        Places a market order. `side` is 'buy' or 'sell'.
        """
        try:
            response = self.k.query_private('AddOrder', {
                'pair': pair,
                'type': side,
                'ordertype': order_type,
                'volume': volume
            })
            if response.get('error'):
                print(f"[!] Kraken API error: {response['error']}")
            else:
                print(f"[✓] Order placed: {side} {volume} {pair}")
            return response
        except Exception as e:
            print(f"[!] Error placing order: {e}")
            return None

    def get_open_orders(self):
        try:
            return self.kraken.get_open_orders()[0]
        except Exception as e:
            print(f"[!] Error fetching open orders: {e}")
            return None
