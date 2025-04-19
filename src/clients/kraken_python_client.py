# clients/kraken_python_client.py
from rust_kraken_client import get_bid, get_ask

class KrakenPythonClient:
    def get_bid(self):
        return get_bid()
    def get_ask(self):
        return get_ask()
