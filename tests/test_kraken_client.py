import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.clients.kraken_sync_client import KrakenSyncClient

def test_get_bid():
    try:
        client = KrakenSyncClient()
        print(client.get_balance())
    except Exception as e:
        print(f"[Error] KrakenSyncClient.get_bid() Failed: {e}")

if __name__ == "__main__":
    test_get_bid()