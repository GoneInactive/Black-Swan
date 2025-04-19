# tests/test_api.py

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from kraken_api import KrakenClient

async def test_balance():
    try:
        print("\n Testing get_balance()")
        client = KrakenClient()
        balance = await client.get_balance()
        print(balance)
        await client.close()
        return 0
    except Exception as e:
        print(f'[ERROR] Test Failed: {e}')
        return 1

async def test_order_book():
    print("\n Testing get_order_book()")
    client = KrakenClient()
    try:
        order_book = await client.get_orderbook(depth=10)
        
        print(order_book)

        if order_book:
            print("\nTop 5 Asks:")
            for ask in reversed(order_book['asks'][:5]):
                print(f"Price: ${ask[0]} | Volume: {ask[1]} | Timestamp: {ask[2]}")

            print("Top 5 Bids:")
            for bid in order_book['bids'][:5]:
                print(f"Price: ${bid[0]} | Volume: {bid[1]} | Timestamp: {bid[2]}")

            print(f"Spread: ${round(float(order_book['asks'][:5][0][0])-float(order_book['bids'][:5][0][0]),6)}")
            return 0
        else:
            print("[!] No order book data returned.")
            return 1
    except Exception as e:
        print(f"[ERROR] get_order_book failed: {e}")
        return 1
    finally:
        await client.close()
    
async def test_clean_order_book():
    print("\n Testing get_clean_order_book()")
    client = KrakenClient()
    try:
        order_book = await client.get_clean_orderbook()
        print(order_book)
        if order_book == None:
            print(f"[ERROR] get_clean_orderbook() failed: {e}")
            return 1
        return 0
    except Exception as e:
        print(f"[ERROR] get_clean_orderbook() failed: {e}")
        return 1
    finally:
        await client.close()

# async def test_get_ask():
#     print("\n Testing get_ask()")
#     client = KrakenClient()
#     try:
#         ask = await client.get_ask()
#         print(ask)
#         return 0
    
#     except Exception as e:
#         print(f"[ERROR] get_ask() failed: {e}")
#         return 1

#     finally:
#         await client.close()

# async def test_get_bid():
#     print("\n Testing get_bid()")
#     client = KrakenClient()
#     try:
#         bid = await client.get_bid()
#         print(bid)
#         return 0
    
#     except Exception as e:
#         print(f"[ERROR] get_bid() failed: {e}")
#         return 1

#     finally:
#         await client.close()


if __name__ == "__main__":
    fails = 0
    tests = 3
    fails+=asyncio.run(test_balance())
    fails+=asyncio.run(test_order_book())
    fails+=asyncio.run(test_clean_order_book())

    print("-"*20)
    print('Test Complete.')
    print(f"Tests Passed: {tests-fails}")
    print(f"Tests Failed: {fails}")
    print("-"*20)
