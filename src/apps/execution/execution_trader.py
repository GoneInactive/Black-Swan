import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "clients")))
from kraken_python_client import KrakenPythonClient


class SmartTrader:
    def __init__(self, asset=None):
        self.exchanges_tradable = []
        self.client = KrakenPythonClient()
        if self.client.test_connection():
            self.exchanges_tradable.append('Kraken')

    def __execute__(self):
        return