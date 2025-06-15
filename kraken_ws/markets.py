from typing import List, Callable, Optional, Dict, Any, Tuple
import logging
import time
from .kraken_ws import KrakenWebSocket
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    pair: str
    data: Any
    timestamp: float

class KrakenMarkets:
    """
    Kraken WebSocket client for market data operations.
    """
    
    def __init__(self, client: KrakenWebSocket):
        self.client = client
        self._subscriptions = set()
        
    def subscribe_ticker(self, pairs: List[str], callback: Callable = None) -> None:
        """Subscribe to ticker data for specified trading pairs."""
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
        self._subscriptions.add(f"ticker:{','.join(pairs)}")
        logger.info(f"Subscribed to ticker for pairs: {pairs}")
    
    def subscribe_ohlc(self, pairs: List[str], interval: int = 1, callback: Callable = None) -> None:
        """Subscribe to OHLC (candlestick) data."""
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
        self._subscriptions.add(f"ohlc:{interval}:{','.join(pairs)}")
        logger.info(f"Subscribed to OHLC-{interval} for pairs: {pairs}")
    
    def subscribe_trade(self, pairs: List[str], callback: Callable = None) -> None:
        """Subscribe to trade data."""
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
        self._subscriptions.add(f"trade:{','.join(pairs)}")
        logger.info(f"Subscribed to trades for pairs: {pairs}")
    
    def subscribe_book(self, pairs: List[str], depth: int = 10, callback: Callable = None) -> None:
        """Subscribe to order book data."""
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
        self._subscriptions.add(f"book:{depth}:{','.join(pairs)}")
        logger.info(f"Subscribed to order book-{depth} for pairs: {pairs}")
    
    def subscribe_spread(self, pairs: List[str], callback: Callable = None) -> None:
        """Subscribe to spread data."""
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
        self._subscriptions.add(f"spread:{','.join(pairs)}")
        logger.info(f"Subscribed to spread for pairs: {pairs}")
    
    def get_orderbook(self, pair: str) -> Optional[MarketData]:
        """Get the current orderbook for a pair."""
        orderbook = self.client.get_orderbook(pair)
        if not orderbook:
            return None
        return MarketData(
            pair=pair,
            data={
                'asks': orderbook.asks,
                'bids': orderbook.bids
            },
            timestamp=orderbook.timestamp
        )
    
    def get_ticker(self, pair: str) -> Optional[MarketData]:
        """Get the current ticker for a pair."""
        ticker = self.client.get_ticker(pair)
        if not ticker:
            return None
        return MarketData(
            pair=pair,
            data=ticker,
            timestamp=time.time()
        )
    
    def unsubscribe_all(self) -> None:
        """Unsubscribe from all market data feeds."""
        for sub in list(self._subscriptions):
            parts = sub.split(':')
            if parts[0] == 'ticker':
                self.unsubscribe_ticker(parts[1].split(','))
            elif parts[0] == 'ohlc':
                self.unsubscribe_ohlc(parts[2].split(','), int(parts[1]))
            elif parts[0] == 'trade':
                self.unsubscribe_trade(parts[1].split(','))
            elif parts[0] == 'book':
                self.unsubscribe_book(parts[2].split(','), int(parts[1]))
            elif parts[0] == 'spread':
                self.unsubscribe_spread(parts[1].split(','))
    
    def unsubscribe_ticker(self, pairs: List[str]) -> None:
        """Unsubscribe from ticker data."""
        self._unsubscribe(pairs, "ticker")
    
    def unsubscribe_ohlc(self, pairs: List[str], interval: int = 1) -> None:
        """Unsubscribe from OHLC data."""
        self._unsubscribe(pairs, "ohlc", {"interval": interval})
    
    def unsubscribe_trade(self, pairs: List[str]) -> None:
        """Unsubscribe from trade data."""
        self._unsubscribe(pairs, "trade")
    
    def unsubscribe_book(self, pairs: List[str], depth: int = 10) -> None:
        """Unsubscribe from order book data."""
        self._unsubscribe(pairs, "book", {"depth": depth})
    
    def unsubscribe_spread(self, pairs: List[str]) -> None:
        """Unsubscribe from spread data."""
        self._unsubscribe(pairs, "spread")
    
    def _unsubscribe(self, pairs: List[str], name: str, params: Optional[dict] = None) -> None:
        """Helper method for unsubscribing."""
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        subscription = {"name": name}
        if params:
            subscription.update(params)
            
        unsubscription = {
            "event": "unsubscribe",
            "pair": pairs,
            "subscription": subscription
        }
        
        self.client.send_message(unsubscription)
        key_parts = [name]
        if params and 'interval' in params:
            key_parts.append(str(params['interval']))
        if params and 'depth' in params:
            key_parts.append(str(params['depth']))
        key_parts.append(','.join(pairs))
        self._subscriptions.discard(':'.join(key_parts))
        logger.info(f"Unsubscribed from {name} for pairs: {pairs}")

# Parsing functions
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

def parse_book_data(data: dict) -> dict:
    """
    Parse raw order book data into a more usable format.
    
    Args:
        data: Raw order book data from WebSocket
        
    Returns:
        Parsed order book data dictionary with 'asks' and 'bids' lists
    """
    return {
        'asks': [(float(price), float(volume), float(timestamp)) for price, volume, timestamp in data.get('as', [])],
        'bids': [(float(price), float(volume), float(timestamp)) for price, volume, timestamp in data.get('bs', [])],
        'asks_all': data.get('a', []),  # Raw asks data
        'bids_all': data.get('b', []),  # Raw bids data
        'checksum': data.get('c', None)  # Checksum if available
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

def parse_spread_data(data: list) -> dict:
    """
    Parse raw spread data into a more usable format.
    
    Args:
        data: Raw spread data from WebSocket
        
    Returns:
        Parsed spread data dictionary
    """
    return {
        'bid': float(data[0]),
        'ask': float(data[1]),
        'time': float(data[2]),
        'bid_volume': float(data[3]),
        'ask_volume': float(data[4])
    }