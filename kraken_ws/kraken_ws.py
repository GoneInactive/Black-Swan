import asyncio
import json
import websockets
import logging
from typing import Dict, List, Callable, Optional, Any
from pathlib import Path
import yaml
import hashlib
import hmac
import base64
import time
import urllib.parse

from account import KrakenAccount
from markets import KrakenMarkets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KrakenWebSocket:
    """
    Kraken WebSocket client for real-time data streaming and trading.
    """
    
    WS_PUBLIC_URL = "wss://ws.kraken.com/"
    WS_PRIVATE_URL = "wss://ws-auth.kraken.com/"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = None
        self.api_secret = None
        self._load_credentials(api_key, api_secret)
        
        self.public_ws = None
        self.private_ws = None
        self.is_connected = False
        self.is_authenticated = False
        
        # Message handlers
        self.handlers: Dict[str, List[Callable]] = {}
        
        # Subscription tracking
        self.subscriptions: Dict[str, Dict] = {}
        
        # Initialize components
        self.account = KrakenAccount(self.api_key, self.api_secret)
        self.markets = KrakenMarkets()
        
        # Connection management
        self._running = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        
    def _load_credentials(self, api_key: Optional[str], api_secret: Optional[str]):
        """Load API credentials from config file or parameters."""
        current_file = Path(__file__)
        config_path = current_file.parent.parent / "config" / "config.yaml"
        config = self._load_config(config_path)
        
        self.api_key = api_key or config.get('kraken', {}).get('api_key')
        self.api_secret = api_secret or config.get('kraken', {}).get('api_secret')
        
        if not self.api_key or not self.api_secret:
            logger.warning("API credentials not found. Private endpoints will not be available.")
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config: {e}")
            return {}
    
    def _generate_auth_token(self) -> str:
        """Generate authentication token for private WebSocket."""
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials required for authentication")
            
        nonce = str(int(time.time() * 1000))
        message = nonce + nonce
        
        # Create signature
        secret_bytes = base64.b64decode(self.api_secret)
        message_bytes = message.encode('utf-8')
        signature = hmac.new(secret_bytes, message_bytes, hashlib.sha512)
        signature_b64 = base64.b64encode(signature.digest()).decode()
        
        return signature_b64
    
    async def connect(self, private: bool = False):
        """Connect to Kraken WebSocket."""
        try:
            if private and (not self.api_key or not self.api_secret):
                raise ValueError("API credentials required for private connection")
            
            url = self.WS_PRIVATE_URL if private else self.WS_PUBLIC_URL
            
            if private:
                self.private_ws = await websockets.connect(url)
                await self._authenticate()
                logger.info("Connected to Kraken private WebSocket")
            else:
                self.public_ws = await websockets.connect(url)
                logger.info("Connected to Kraken public WebSocket")
            
            self.is_connected = True
            self._reconnect_attempts = 0
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            raise
    
    async def _authenticate(self):
        """Authenticate private WebSocket connection."""
        if not self.private_ws:
            raise ValueError("Private WebSocket not connected")
        
        try:
            token = self._generate_auth_token()
            auth_message = {
                "event": "subscribe",
                "subscription": {
                    "name": "ownTrades",
                    "token": token
                }
            }
            
            await self.private_ws.send(json.dumps(auth_message))
            self.is_authenticated = True
            logger.info("Authenticated with Kraken private WebSocket")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def add_handler(self, event_type: str, handler: Callable):
        """Add message handler for specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Added handler for {event_type}")
    
    def remove_handler(self, event_type: str, handler: Callable):
        """Remove message handler."""
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
    
    async def subscribe_ticker(self, pairs: List[str], handler: Optional[Callable] = None):
        """Subscribe to ticker updates."""
        if handler:
            self.add_handler('ticker', handler)
        
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "ticker"}
        }
        
        await self._send_subscription(subscription, is_private=False)
        self.subscriptions['ticker'] = subscription
        logger.info(f"Subscribed to ticker for pairs: {pairs}")
    
    async def subscribe_ohlc(self, pairs: List[str], interval: int = 1, handler: Optional[Callable] = None):
        """Subscribe to OHLC (candlestick) data."""
        if handler:
            self.add_handler('ohlc', handler)
        
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "ohlc", "interval": interval}
        }
        
        await self._send_subscription(subscription, is_private=False)
        self.subscriptions['ohlc'] = subscription
        logger.info(f"Subscribed to OHLC for pairs: {pairs}, interval: {interval}")
    
    async def subscribe_trade(self, pairs: List[str], handler: Optional[Callable] = None):
        """Subscribe to trade data."""
        if handler:
            self.add_handler('trade', handler)
        
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "trade"}
        }
        
        await self._send_subscription(subscription, is_private=False)
        self.subscriptions['trade'] = subscription
        logger.info(f"Subscribed to trades for pairs: {pairs}")
    
    async def subscribe_book(self, pairs: List[str], depth: int = 10, handler: Optional[Callable] = None):
        """Subscribe to order book data."""
        if handler:
            self.add_handler('book', handler)
        
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "book", "depth": depth}
        }
        
        await self._send_subscription(subscription, is_private=False)
        self.subscriptions['book'] = subscription
        logger.info(f"Subscribed to order book for pairs: {pairs}, depth: {depth}")
    
    async def subscribe_own_trades(self, handler: Optional[Callable] = None):
        """Subscribe to own trades (private)."""
        if not self.is_authenticated:
            await self.connect(private=True)
        
        if handler:
            self.add_handler('ownTrades', handler)
        
        # Authentication already subscribes to ownTrades
        logger.info("Subscribed to own trades")
    
    async def subscribe_open_orders(self, handler: Optional[Callable] = None):
        """Subscribe to open orders (private)."""
        if not self.is_authenticated:
            await self.connect(private=True)
        
        if handler:
            self.add_handler('openOrders', handler)
        
        subscription = {
            "event": "subscribe",
            "subscription": {"name": "openOrders"}
        }
        
        await self._send_subscription(subscription, is_private=True)
        self.subscriptions['openOrders'] = subscription
        logger.info("Subscribed to open orders")
    
    async def _send_subscription(self, subscription: Dict, is_private: bool = False):
        """Send subscription message to appropriate WebSocket."""
        ws = self.private_ws if is_private else self.public_ws
        
        if not ws:
            if is_private:
                await self.connect(private=True)
                ws = self.private_ws
            else:
                await self.connect(private=False)
                ws = self.public_ws
        
        await ws.send(json.dumps(subscription))
    
    async def _handle_message(self, message: str, is_private: bool = False):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            
            # Handle different message types
            if isinstance(data, dict):
                if 'event' in data:
                    await self._handle_event_message(data)
                elif 'errorMessage' in data:
                    logger.error(f"WebSocket error: {data['errorMessage']}")
            elif isinstance(data, list) and len(data) >= 2:
                await self._handle_data_message(data)
            
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _handle_event_message(self, data: Dict):
        """Handle event messages (subscriptions, heartbeats, etc.)."""
        event = data.get('event')
        
        if event == 'heartbeat':
            logger.debug("Received heartbeat")
        elif event == 'systemStatus':
            logger.info(f"System status: {data.get('status')}")
        elif event == 'subscriptionStatus':
            status = data.get('status')
            subscription = data.get('subscription', {}).get('name', 'unknown')
            logger.info(f"Subscription {subscription}: {status}")
        
        # Call registered handlers
        if event in self.handlers:
            for handler in self.handlers[event]:
                try:
                    await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                except Exception as e:
                    logger.error(f"Error in {event} handler: {e}")
    
    async def _handle_data_message(self, data: List):
        """Handle data messages (ticker, trades, etc.)."""
        try:
            channel_name = data[-2]  # Channel name is second to last element
            pair = data[-1] if len(data) > 2 else None
            
            # Determine message type and call appropriate handlers
            if 'ticker' in channel_name:
                if 'ticker' in self.handlers:
                    for handler in self.handlers['ticker']:
                        try:
                            await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                        except Exception as e:
                            logger.error(f"Error in ticker handler: {e}")
            
            elif 'ohlc' in channel_name:
                if 'ohlc' in self.handlers:
                    for handler in self.handlers['ohlc']:
                        try:
                            await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                        except Exception as e:
                            logger.error(f"Error in OHLC handler: {e}")
            
            elif 'trade' in channel_name:
                if 'trade' in self.handlers:
                    for handler in self.handlers['trade']:
                        try:
                            await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                        except Exception as e:
                            logger.error(f"Error in trade handler: {e}")
            
            elif 'book' in channel_name:
                if 'book' in self.handlers:
                    for handler in self.handlers['book']:
                        try:
                            await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                        except Exception as e:
                            logger.error(f"Error in book handler: {e}")
            
            elif channel_name == 'ownTrades':
                if 'ownTrades' in self.handlers:
                    for handler in self.handlers['ownTrades']:
                        try:
                            await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                        except Exception as e:
                            logger.error(f"Error in ownTrades handler: {e}")
            
            elif channel_name == 'openOrders':
                if 'openOrders' in self.handlers:
                    for handler in self.handlers['openOrders']:
                        try:
                            await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                        except Exception as e:
                            logger.error(f"Error in openOrders handler: {e}")
                            
        except Exception as e:
            logger.error(f"Error processing data message: {e}")
    
    async def run(self):
        """Run the WebSocket client."""
        self._running = True
        
        try:
            # Start public connection by default
            if not self.public_ws:
                await self.connect(private=False)
            
            tasks = []
            
            # Listen to public WebSocket
            if self.public_ws:
                tasks.append(asyncio.create_task(self._listen(self.public_ws, is_private=False)))
            
            # Listen to private WebSocket if connected
            if self.private_ws:
                tasks.append(asyncio.create_task(self._listen(self.private_ws, is_private=True)))
            
            # Wait for all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error in run loop: {e}")
            if self._reconnect_attempts < self._max_reconnect_attempts:
                self._reconnect_attempts += 1
                logger.info(f"Attempting reconnection {self._reconnect_attempts}/{self._max_reconnect_attempts}")
                await asyncio.sleep(5)
                await self.run()
    
    async def _listen(self, ws, is_private: bool = False):
        """Listen to WebSocket messages."""
        try:
            async for message in ws:
                if not self._running:
                    break
                await self._handle_message(message, is_private)
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"{'Private' if is_private else 'Public'} WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in WebSocket listener: {e}")
    
    async def close(self):
        """Close WebSocket connections."""
        self._running = False
        
        if self.public_ws:
            await self.public_ws.close()
            logger.info("Closed public WebSocket connection")
        
        if self.private_ws:
            await self.private_ws.close()
            logger.info("Closed private WebSocket connection")
        
        self.is_connected = False
        self.is_authenticated = False
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.is_connected:
            asyncio.create_task(self.close())