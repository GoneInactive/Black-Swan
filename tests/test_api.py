# tests/test_api.py

import sys
import os
import time
import yaml
import pprint

# Dynamically add src/ to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from kraken_api import KrakenClient

# Load config.yaml from project-root/config/config.yaml
def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"))
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

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
        pair = f"{config['trade']['base_asset']}{config['trade']['quote_asset']}"
        df = client.get_ohlc(pair=pair, interval=60)
        print(df.head())
    except Exception as e:
        print(f"[ERROR] get_ohlc failed: {e}")

def test_ticker():
    print("\n💹 Testing get_ticker()")
    try:
        pair = f"{config['trade']['base_asset']}Z{config['trade']['quote_asset']}"
        ticker = client.get_orderbook(pair)
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
Run with:
python tests/test_api.py
'''
