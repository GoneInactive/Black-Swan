import os
import sys

# Import setup for API client
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    clients_path = os.path.join(current_dir, "../../..", "src", "clients")
    sys.path.insert(0, os.path.abspath(clients_path))
except NameError:
    current_dir = os.getcwd()
    base_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "src", "clients"))
    sys.path.insert(0, base_path)
except Exception as e:
    print(e)

from kraken_python_client import KrakenPythonClient

asset = "EURQ"
ref_asset = "EUR"
total_capital = 1000
max_per_order = 250

def main():
    client = KrakenPythonClient()
    eurusd = client.get_bid('EURUSD')
    eurq_balance = client.get_balance(asset)
    eurq_value = eurq_balance * client.get_bid('EURQUSD')
    eur_balance = total_capital - eurq_value
    imbalance = (eurq_value - eur_balance) / total_capital

    bid_price = client.get_bid('EURQUSD')
    ask_price = client.get_ask('EURQUSD')

    bid_bias = max(0.5 - imbalance, 0)
    ask_bias = max(0.5 + imbalance, 0)

    bid_size_raw = min(max_per_order / bid_price * bid_bias, eur_balance / bid_price)
    ask_size_raw = min(max_per_order / ask_price * ask_bias, eurq_balance)

    bid_size = round(max(bid_size_raw, 100), 6)
    ask_size = round(max(ask_size_raw, 100), 6)

    return bid_size, ask_size


if __name__ == "__main__":
    print(main())