import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "src", "clients")))

from kraken_python_client import KrakenPythonClient



def main():
    client = KrakenPythonClient()
    order = (client.add_order('EURRUSD','buy',1,5))
    order_id = order['txid']
    print(client.get_open_orders('EURRUSD'))


if __name__ == "__main__":
    main()