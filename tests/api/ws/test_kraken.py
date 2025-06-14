import sys
import os
import time
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from kraken_ws import KrakenWebSocket
from kraken_ws.markets import KrakenMarkets
from kraken_ws.account import KrakenAccount


def main():
    # Initialize client
    client = KrakenWebSocket()

    # Initialize market data and account modules
    markets = KrakenMarkets(client)
    account = KrakenAccount(client)

    # Connect
    client.open()

    # Subscribe to market data
    markets.subscribe_ticker(['BTC/USD'])

    # Place orders (requires authentication)
    account.add_order('BTC/USD', 'buy', 'market', '0.001')

    # Close connection
    client.close()

if __name__ == "__main__":
    main()