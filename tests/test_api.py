# tests/test_api.py

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from kraken_api import KrakenClient

async def test_balance():
    print("\n Testing get_balance()")
    client = KrakenClient()
    balance = await client.get_balance()
    print(balance)
    await client.close()

async def test_order_book():
    print("\n Testing get_order_book()")
    client = KrakenClient()
    try:
        order_book = await client.get_orderbook(depth=10)
        
        if order_book:
            print("\nTop 5 Asks:")
            for ask in reversed(order_book['asks'][:5]):
                print(f"Price: ${ask[0]} | Volume: {ask[1]} | Timestamp: {ask[2]}")

            print("Top 5 Bids:")
            for bid in order_book['bids'][:5]:
                print(f"Price: ${bid[0]} | Volume: {bid[1]} | Timestamp: {bid[2]}")

            print(f"Spread: ${round(float(order_book['asks'][:5][0][0])-float(order_book['bids'][:5][0][0]),6)}")
        else:
            print("[!] No order book data returned.")
    except Exception as e:
        print(f"[ERROR] get_order_book failed: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_balance())
    asyncio.run(test_order_book())
