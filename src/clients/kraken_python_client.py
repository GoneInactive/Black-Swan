from rust_kraken_client import rust_kraken_client as kraken
"""
This client is used to interact with the kraken API built in rust.
"""
class KrakenPythonClient:
    def __init__(self,asset=None):
        self.asset = asset

    def get_bid(self,asset=None):
        """
        Get the bid price of an asset.
        """
        return kraken.get_bid()
    
    def get_ask(self,asset=None):
        """
        Get the ask price of an asset.
        """
        return kraken.get_ask()
    
    def get_balance(self,asset="*"):
        """
        Get the balance of an asset.
        If asset is "*", returns all balances.
        """
        if asset == "*":
            # Returns all balances
            return kraken.get_balance()
        else:
            # Returns specific balance
            return kraken.get_balance()[asset]
        
    def get_spread(self,asset=None):
        """
        Get the spread of an asset.
        """
        return kraken.get_spread()
    
    def add_order(self,asset,side,price,volume):
        order_response = kraken.add_order(asset, side, price, volume)

    def get_orders(self):
        pass
        
