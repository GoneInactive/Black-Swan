import sys
import os
try:
    import rust_kraken_client
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../rust_client/target/debug')))  # or target/release if built in release mode
    import rust_kraken_client
import json

def test_kraken():
    results = {}
    try:
        results['bid'] = rust_kraken_client.get_bid()
        results['ask'] = rust_kraken_client.get_ask()
        results['spread'] = rust_kraken_client.get_spread()
        results['balance'] = rust_kraken_client.get_balance()
    except Exception as e:
        results['error'] = str(e)
    return results

def test_binance():
    results = {}
    try:
        depth_json = rust_kraken_client.get_binance_depth()
        depth_data = json.loads(depth_json)
        results['bids_count'] = len(depth_data.get('bids', []))
        results['asks_count'] = len(depth_data.get('asks', []))
        results['top_bid'] = depth_data['bids'][0] if depth_data['bids'] else None
        results['top_ask'] = depth_data['asks'][0] if depth_data['asks'] else None
    except Exception as e:
        results['error'] = str(e)
    return results

if __name__ == "__main__":
    kraken_results = test_kraken()
    binance_results = test_binance()

    print("Kraken API Results:")
    for key, value in kraken_results.items():
        print(f"{key}: {value}")

    print("\nBinance API Results:")
    for key, value in binance_results.items():
        print(f"{key}: {value}")
