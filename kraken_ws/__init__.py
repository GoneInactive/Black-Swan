"""
Kraken WebSocket API Client

A comprehensive Python client for the Kraken WebSocket API supporting both
market data and authenticated account operations.

Usage:
    from kraken_ws import KrakenWebSocket
    from kraken_ws.markets import KrakenMarkets
    from kraken_ws.account import KrakenAccount
    
    # Initialize client
    client = KrakenWebSocket(api_key="your_key", api_secret="your_secret")
    
    # Initialize market data and account modules
    markets = KrakenMarkets(client)
    account = KrakenAccount(client)
    
    # Connect
    client.open()
    
    # Subscribe to market data
    markets.subscribe_ticker(['BTC/USD'])
    
    # Place orders (requires authentication)
    account.add_order('BTC/USD', 'buy', 'market', '0.001')
    
    # Close connection
    client.close()
"""

from .kraken_ws import KrakenWebSocket
from .markets import KrakenMarkets, parse_ticker_data, parse_ohlc_data, parse_trade_data
from .account import KrakenAccount, OrderManager, parse_own_trades, parse_open_orders

__all__ = [
    # Core client
    'KrakenWebSocket',
    
    # Market data
    'KrakenMarkets',
    'parse_ticker_data',
    'parse_ohlc_data', 
    'parse_trade_data',
    
    # Account operations
    'KrakenAccount',
    'OrderManager',
    'parse_own_trades',
    'parse_open_orders'
]


class KrakenClient:
    """
    Convenience wrapper that combines WebSocket client, markets, and account functionality.
    
    This provides a single interface for all Kraken WebSocket operations.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Initialize the complete Kraken client.
        
        Args:
            api_key: Optional Kraken API key for authenticated operations
            api_secret: Optional Kraken API secret for authenticated operations
        """
        self.ws = KrakenWebSocket(api_key=api_key, api_secret=api_secret)
        self.markets = KrakenMarkets(self.ws)
        self.account = KrakenAccount(self.ws) if api_key and api_secret else None
        self.order_manager = OrderManager(self.account) if self.account else None
        
    def open(self) -> None:
        """Open WebSocket connection."""
        self.ws.open()
        
    def close(self) -> None:
        """Close WebSocket connection."""
        self.ws.close()
        
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    @property
    def connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.ws.connected