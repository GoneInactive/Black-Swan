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
    data = markets.get_orderbook('BTC/USD')

    # Place orders (requires authentication)
    account.add_order('EURQ/USD', 'buy', 'limit', '10', '1') ## Have this return some info about it, including the order id

    account.edit_order(...)

    ## etc..

    # Close connection
    client.close()

if __name__ == "__main__":
    main()