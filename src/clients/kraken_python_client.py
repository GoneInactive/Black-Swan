from rust_kraken_client import rust_kraken_client as kraken

class KrakenPythonClient:
    def get_bid(self,asset):
        return kraken.get_bid(asset)
    
    def get_ask(self,asset):
        return kraken.get_ask(asset)
    
    def get_balance(self,asset="*")
        if asset == "*":
            return kraken.get_balance()
        else:
            return kraken.get_balance(asset)
        
    def get_spread(self,asset):
        return kraken.get_spread(asset)
        
