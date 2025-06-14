from typing import List, Callable, Optional
import logging
from .kraken_ws import KrakenWebSocket

logger = logging.getLogger(__name__)


class KrakenMarkets:
    """
    Kraken WebSocket client for market data operations.
    
    Handles subscriptions to various market data feeds including:
    - Ticker data
    - Trade data
    - OHLC/Candlestick data
    - Order book data
    - Spread data
    """
    
    def __init__(self, client: KrakenWebSocket):
        """
        Initialize the markets client.
        
        Args:
            client: KrakenWebSocket instance to use for communication
        """
        self.client = client
        
    def subscribe_ticker(self, pairs: List[str], callback: Callable = None) -> None:
        """
        Subscribe to ticker data for specified trading pairs.
        
        Args:
            pairs: List of trading pairs (e.g., ['BTC/USD', 'ETH/USD'])
            callback: Optional callback function to handle ticker data
                     Signature: callback(pair: str, data: dict)
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        if callback:
            self.client.add_message_handler('ticker', callback)
            
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "ticker"}
        }
        
        self.client.send_message(subscription)
        self.client.subscriptions.add(f"ticker:{','.join(pairs)}")
        logger.info(f"Subscribed to ticker for pairs: {pairs}")
    
    def subscribe_ohlc(self, pairs: List[str], interval: int = 1, callback: Callable = None) -> None:
        """
        Subscribe to OHLC (candlestick) data.
        
        Args:
            pairs: List of trading pairs
            interval: Time interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
            callback: Optional callback function to handle OHLC data
                     Signature: callback(pair: str, data: dict)
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        valid_intervals = [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval. Must be one of: {valid_intervals}")
            
        if callback:
            self.client.add_message_handler('ohlc', callback)
            
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "ohlc", "interval": interval}
        }
        
        self.client.send_message(subscription)
        self.client.subscriptions.add(f"ohlc:{interval}:{','.join(pairs)}")
        logger.info(f"Subscribed to OHLC-{interval} for pairs: {pairs}")
    
    def subscribe_trade(self, pairs: List[str], callback: Callable = None) -> None:
        """
        Subscribe to trade data.
        
        Args:
            pairs: List of trading pairs
            callback: Optional callback function to handle trade data
                     Signature: callback(pair: str, data: list)
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        if callback:
            self.client.add_message_handler('trade', callback)
            
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "trade"}
        }
        
        self.client.send_message(subscription)
        self.client.subscriptions.add(f"trade:{','.join(pairs)}")
        logger.info(f"Subscribed to trades for pairs: {pairs}")
    
    def subscribe_book(self, pairs: List[str], depth: int = 10, callback: Callable = None) -> None:
        """
        Subscribe to order book data.
        
        Args:
            pairs: List of trading pairs
            depth: Order book depth (10, 25, 100, 500, 1000)
            callback: Optional callback function to handle book data
                     Signature: callback(pair: str, data: dict)
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        valid_depths = [10, 25, 100, 500, 1000]
        if depth not in valid_depths:
            raise ValueError(f"Invalid depth. Must be one of: {valid_depths}")
            
        if callback:
            self.client.add_message_handler('book', callback)
            
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "book", "depth": depth}
        }
        
        self.client.send_message(subscription)
        self.client.subscriptions.add(f"book:{depth}:{','.join(pairs)}")
        logger.info(f"Subscribed to order book-{depth} for pairs: {pairs}")
    
    def subscribe_spread(self, pairs: List[str], callback: Callable = None) -> None:
        """
        Subscribe to spread data.
        
        Args:
            pairs: List of trading pairs
            callback: Optional callback function to handle spread data
                     Signature: callback(pair: str, data: list)
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        if callback:
            self.client.add_message_handler('spread', callback)
            
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "spread"}
        }
        
        self.client.send_message(subscription)
        self.client.subscriptions.add(f"spread:{','.join(pairs)}")
        logger.info(f"Subscribed to spread for pairs: {pairs}")
    
    def unsubscribe_ticker(self, pairs: List[str]) -> None:
        """
        Unsubscribe from ticker data.
        
        Args:
            pairs: List of trading pairs to unsubscribe from
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        unsubscription = {
            "event": "unsubscribe",
            "pair": pairs,
            "subscription": {"name": "ticker"}
        }
        
        self.client.send_message(unsubscription)
        self.client.subscriptions.discard(f"ticker:{','.join(pairs)}")
        logger.info(f"Unsubscribed from ticker for pairs: {pairs}")
    
    def unsubscribe_ohlc(self, pairs: List[str], interval: int = 1) -> None:
        """
        Unsubscribe from OHLC data.
        
        Args:
            pairs: List of trading pairs to unsubscribe from
            interval: Time interval that was subscribed to
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        unsubscription = {
            "event": "unsubscribe",
            "pair": pairs,
            "subscription": {"name": "ohlc", "interval": interval}
        }
        
        self.client.send_message(unsubscription)
        self.client.subscriptions.discard(f"ohlc:{interval}:{','.join(pairs)}")
        logger.info(f"Unsubscribed from OHLC-{interval} for pairs: {pairs}")
    
    def unsubscribe_trade(self, pairs: List[str]) -> None:
        """
        Unsubscribe from trade data.
        
        Args:
            pairs: List of trading pairs to unsubscribe from
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        unsubscription = {
            "event": "unsubscribe",
            "pair": pairs,
            "subscription": {"name": "trade"}
        }
        
        self.client.send_message(unsubscription)
        self.client.subscriptions.discard(f"trade:{','.join(pairs)}")
        logger.info(f"Unsubscribed from trades for pairs: {pairs}")
    
    def unsubscribe_book(self, pairs: List[str], depth: int = 10) -> None:
        """
        Unsubscribe from order book data.
        
        Args:
            pairs: List of trading pairs to unsubscribe from
            depth: Order book depth that was subscribed to
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        unsubscription = {
            "event": "unsubscribe",
            "pair": pairs,
            "subscription": {"name": "book", "depth": depth}
        }
        
        self.client.send_message(unsubscription)
        self.client.subscriptions.discard(f"book:{depth}:{','.join(pairs)}")
        logger.info(f"Unsubscribed from order book-{depth} for pairs: {pairs}")
    
    def unsubscribe_spread(self, pairs: List[str]) -> None:
        """
        Unsubscribe from spread data.
        
        Args:
            pairs: List of trading pairs to unsubscribe from
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        unsubscription = {
            "event": "unsubscribe",
            "pair": pairs,
            "subscription": {"name": "spread"}
        }
        
        self.client.send_message(unsubscription)
        self.client.subscriptions.discard(f"spread:{','.join(pairs)}")
        logger.info(f"Unsubscribed from spread for pairs: {pairs}")


def parse_ticker_data(data: dict) -> dict:
    """
    Parse raw ticker data into a more usable format.
    
    Args:
        data: Raw ticker data from WebSocket
        
    Returns:
        Parsed ticker data dictionary
    """
    return {
        'ask': float(data['a'][0]),
        'bid': float(data['b'][0]),
        'last': float(data['c'][0]),
        'volume': float(data['v'][1]),
        'vwap': float(data['p'][1]),
        'high': float(data['h'][1]),
        'low': float(data['l'][1]),
        'open': float(data['o'][1])
    }


def parse_ohlc_data(data: list) -> dict:
    """
    Parse raw OHLC data into a more usable format.
    
    Args:
        data: Raw OHLC data from WebSocket
        
    Returns:
        Parsed OHLC data dictionary
    """
    return {
        'time': data[0],
        'open': float(data[1]),
        'high': float(data[2]),
        'low': float(data[3]),
        'close': float(data[4]),
        'vwap': float(data[5]),
        'volume': float(data[6]),
        'count': int(data[7])
    }


def parse_trade_data(data: list) -> list:
    """
    Parse raw trade data into a more usable format.
    
    Args:
        data: Raw trade data from WebSocket
        
    Returns:
        List of parsed trade dictionaries
    """
    return [{
        'price': float(trade[0]),
        'volume': float(trade[1]),
        'time': trade[2],
        'side': trade[3],
        'order_type': trade[4],
        'misc': trade[5]
    } for trade in data]
