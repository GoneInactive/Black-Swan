import asyncio
#from src.kraken_api import KrakenClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from src.kraken_api import KrakenClient
except:
    from kraken_api import KrakenClient

class KrakenSyncClient:
    def __init__(self):
        self.client = KrakenClient()

    def get_bid(self, pair='XXBTZUSD'):
        return asyncio.run(self.client.get_bid(pair))

    def get_ask(self, pair='XXBTZUSD'):
        return asyncio.run(self.client.get_ask(pair))

    def get_balance(self, return_type=''):
        balance = asyncio.run(self.client.get_balance())
        if return_type == 'float':
            return float(balance['ZUSD'][0])
        return asyncio.run(self.client.get_balance())

    def get_clean_orderbook(self, depth=1, pair='XXBTZUSD'):
        return asyncio.run(self.client.get_clean_orderbook(depth=depth, pair=pair))
