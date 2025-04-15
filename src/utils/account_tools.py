import sys
import os
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from kraken_api import KrakenClient


class AccountTools:
    def __init__(self):
        def load_config():
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"))
            with open(config_path, "r") as f:
                return yaml.safe_load(f)

        config = load_config()

        # Initialize Kraken API client
        self.client = KrakenClient(
            api_key=config['kraken']['api_key'],
            api_secret=config['kraken']['api_secret']
        )
    
    def get_balance(self):
        balance = self.client.get_balance()
        return balance
    
    def get_pnl(self):
        return None
