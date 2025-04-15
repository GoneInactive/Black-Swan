# tests/test_api.py

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kraken_api import KrakenClient
import yaml
import pprint

# Load config
with open(os.path.join("..", "config", "config.yaml")) as f:
    config = yaml.safe_load(f)

# Initialize Kraken API client
client = KrakenClient(
    api_key=config['kraken']['api_key'],
    api_secret=config['kraken']['api_secret']
)

def test_balance():
    print("\n📊 Testing get_balance()")
    try:
        balance = client.get_balance()
        pprint.pprint(balance)
    except Exception as e:
        print(f"[ERROR] get_balance failed: {e}")

def test_ohlc():
    print("\n📈 Testing get_ohlc()")
    try:
        pair = f"{config['trade']['base_asset']}Z{config['trade']['quote_asset']}"
        df = client.get_ohlc(pair=pair, interval=60)
        print(df.head())
    except Exception as e:
        print(f"[ERROR] get_ohlc failed: {e}")

def test_ticker():
    print("\n💹 Testing get_ticker()")
    try:
        pair = f"{config['trade']['base_asset']}Z{config['trade']['quote_asset']}"
        ticker = client.get_ticker(pair)
        pprint.pprint(ticker)
    except Exception as e:
        print(f"[ERROR] get_ticker failed: {e}")

if __name__ == "__main__":
    test_balance()
    time.sleep(1)
    test_ohlc()
    time.sleep(1)
    test_ticker()


'''
python tests/test_api.py
'''