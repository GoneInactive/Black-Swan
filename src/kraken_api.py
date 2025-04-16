# src/kraken_api.py

import krakenex
import time
import sys
import os
import yaml

import asyncio
from kraken.spot import SpotAsyncClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

class KrakenClient:
    def __init__(self):
        def load_config():
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"))
            with open(config_path, "r") as f:
                return yaml.safe_load(f)

        config = load_config()

        # Initialize Kraken API client
        self.client = SpotAsyncClient(
            key=config['kraken']['api_key'],
            secret=config['kraken']['api_secret']
        )
    
    async def get_balance(self):
        try:
            response = await self.client.request("POST","/0/private/Balance")
            return response
        finally:
            await self.client.async_close()

    async def get_orderbook(self, depth=3, pair='XXBTZUSD'):
        """
        Get the order book (market depth) for a specific pair.
        `depth` is the number of bid/ask entries to fetch.
        """
        try:
            response = await self.client.request(
            method="GET",
            uri="/0/public/Depth",
            params={
                "pair": pair,
                "count": depth
                }
            )
            ## Price, Volume, Timestamp
            #print(response[pair])
            return response[pair]
        except Exception as e:
            print(f"[!] Error fetching order book: {e}")
            return None

    async def close(self):
        await self.client.async_close()
        return None


    async def get_clean_orderbook(self, depth=1, pair='XXBTZUSD'):
        """
        Fetch a simplified order book from Kraken.

        Args:
            depth (int): Number of price levels to retrieve from the order book.
            pair (str): The trading pair to query (default: 'XXBTZUSD').

        Returns:
            tuple: Two lists — a list of ask prices and a list of bid prices (both as strings).
                Returns ([], []) if no data is available, or None if an error occurs.
        """
        try:
            response = await self.client.request(
                method="GET",
                uri="/0/public/Depth",
                params={"pair": pair, "count": depth}
            )

            asks = [ask[0] for ask in response[pair].get('asks', [])]
            bids = [bid[0] for bid in response[pair].get('bids', [])]

            return asks, bids

        except Exception as e:
            print(f"[ERROR] Fetching simplified order book: {e}")
            return None
