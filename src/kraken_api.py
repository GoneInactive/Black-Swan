# src/kraken_api.py

import os
import sys
import yaml
import asyncio
from kraken.spot import SpotAsyncClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import yaml
import os
import asyncio
from kraken.spot import SpotAsyncClient

class KrakenClient:
    def __init__(self):
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"))
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.api_key = config['kraken']['api_key']
        self.api_secret = config['kraken']['api_secret']

    async def _with_client(self, coro):
        client = SpotAsyncClient(key=self.api_key, secret=self.api_secret)
        try:
            return await coro(client)
        finally:
            await client.async_close()

    async def get_balance(self):
        return await self._with_client(lambda client: client.request("POST", "/0/private/Balance"))

    async def get_clean_orderbook(self, depth=1, pair='XXBTZUSD'):
        async def fetch(client):
            res = await client.request("GET", "/0/public/Depth", params={"pair": pair, "count": depth})
            asks = [ask[0] for ask in res[pair].get('asks', [])]
            bids = [bid[0] for bid in res[pair].get('bids', [])]
            return asks, bids
        return await self._with_client(fetch)

    async def get_ask(self, pair='XXBTZUSD'):
        orderbook = await self.get_clean_orderbook(depth=1, pair=pair)
        return float(orderbook[0][0]) if orderbook and orderbook[0] else None

    async def get_bid(self, pair='XXBTZUSD'):
        orderbook = await self.get_clean_orderbook(depth=1, pair=pair)
        return float(orderbook[1][0]) if orderbook and orderbook[1] else None
