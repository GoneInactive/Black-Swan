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
    It manages public market data streams and delegates private trading
    operations to an instance of KrakenAccount.
    """
    
    WS_PUBLIC_URL = "wss://ws.kraken.com/"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.public_ws = None
        self.is_connected = False
        
        self.handlers: Dict[str, List[Callable]] = {}
        self.subscriptions: Dict[str, Dict] = {}
        
        # Initialize components
        # The account object will manage its own private connection.
        self.account = KrakenAccount(api_key, api_secret)
        self.markets = KrakenMarkets() # Assuming this is for processing market data
        
        self._running = False
        
    async def connect(self, private: bool = False):
        """
        Connects to the necessary WebSocket endpoints.
        - Public connection for market data.
        - Private connection is handled by the account object.
        """
        if not self.public_ws or not self.public_ws.open:
            self.public_ws = await websockets.connect(self.WS_PUBLIC_URL)
            self.is_connected = True
            logger.info("Connected to Kraken public WebSocket for market data.")

        if private:
            # The account object manages its own connection.
            # We just need to ensure it's connected.
            await self.account.connect()
    
    def add_handler(self, event_type: str, handler: Callable):
        """Add a message handler for a specific data type (e.g., 'book')."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Added handler for {event_type}")

    # --- Public Market Data Subscriptions ---

    async def subscribe_book(self, pairs: List[str], depth: int = 10, handler: Optional[Callable] = None):
        """Subscribe to order book data."""
        if handler:
            self.add_handler('book', handler)
        
        subscription = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": "book", "depth": depth}
        }
        
        await self._send_public_subscription(subscription)
        self.subscriptions['book'] = subscription
        logger.info(f"Subscribed to order book for pairs: {pairs}, depth: {depth}")

    async def _send_public_subscription(self, subscription: Dict):
        """Sends a subscription message to the public WebSocket."""
        if not self.is_connected or not self.public_ws:
            await self.connect()
        
        await self.public_ws.send(json.dumps(subscription))

    async def _handle_public_message(self, message: str):
        """Handles incoming public market data messages."""
        try:
            data = json.loads(message)
            
            if isinstance(data, dict) and 'event' in data:
                # Handles subscription status messages, pings, etc.
                logger.debug(f"Received event message: {data}")
                return

            if isinstance(data, list) and len(data) >= 3:
                # This is a data message (e.g., ticker, ohlc, book)
                channel_info = data[2]
                
                # Handle different possible formats for channel_info
                if isinstance(channel_info, str):
                    channel_name = channel_info.split('-')[0]  # 'book' from 'book-10'
                elif isinstance(channel_info, dict) and 'name' in channel_info:
                    channel_name = channel_info['name']
                else:
                    logger.warning(f"Unexpected channel info format: {channel_info}")
                    return
                
                if channel_name in self.handlers:
                    for handler in self.handlers[channel_name]:
                        try:
                            # Call the handler associated with the data type
                            asyncio.create_task(handler(data))
                        except Exception as e:
                            logger.error(f"Error in '{channel_name}' handler: {e}")
            else:
                logger.debug(f"Received message with unexpected format: {data}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode WebSocket message: {e}")
        except Exception as e:
            logger.error(f"Error handling public message: {e}")

    async def run(self):
        """Starts the client and keeps it running."""
        if not self.public_ws:
            raise ConnectionError("Not connected. Call connect() before running.")
            
        self._running = True
        logger.info("KrakenWebSocket client is running...")
        
        try:
            while self._running:
                message = await self.public_ws.recv()
                await self._handle_public_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Public WebSocket connection lost. Exiting run loop.")
        except Exception as e:
            logger.error(f"An error occurred in the run loop: {e}")
        finally:
            self._running = False

    async def close(self):
        """Closes all connections."""
        self._running = False
        
        # Close public connection
        if self.public_ws and self.public_ws.open:
            await self.public_ws.close()
            logger.info("Public WebSocket connection closed.")
            
        # Close private connection via the account object
        await self.account.close()