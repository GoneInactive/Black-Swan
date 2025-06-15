import asyncio
import json
import websockets
import threading
import time
from typing import Dict, List, Callable, Optional, Any
import logging
import yaml
import os
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OrderBookSnapshot:
    asks: List[tuple]  # (price, volume, timestamp)
    bids: List[tuple]  # (price, volume, timestamp)
    pair: str
    timestamp: float

class KrakenWebSocket:
    """
    Core Kraken WebSocket API client for managing connections and message routing.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Initialize the Kraken WebSocket client.
        """
        # Get the path to the config file relative to this file's location
        current_file = Path(__file__)
        config_path = current_file.parent.parent / "config" / "config.yaml"
        
        # Load configuration
        config = self._load_config(config_path)
        
        # Set API credentials from config or parameters
        self.api_key = api_key or config.get('kraken', {}).get('api_key')
        self.api_secret = api_secret or config.get('kraken', {}).get('api_secret')
        
        # Validate that credentials were loaded
        if not self.api_key or not self.api_secret:
            logger.warning("API key and secret not provided - private endpoints will be unavailable")

        # WebSocket URLs
        self.public_url = "wss://ws.kraken.com"
        self.private_url = "wss://ws-auth.kraken.com"
        
        # Connection management
        self.public_ws = None
        self.private_ws = None
        self.is_connected = False
        self.is_running = False
        
        # Event loop and thread management
        self.loop = None
        self.thread = None
        
        # Callback handlers
        self.message_handlers = defaultdict(list)
        self.error_handlers = []
        
        # Subscription tracking
        self.subscriptions = set()
        
        # Data storage
        self.orderbooks = {}
        self.tickers = {}
        self.trades = {}
        
        # Response tracking
        self.pending_responses = {}
        self.response_events = {}
        self.reqid_counter = 0

    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.warning(f"Error parsing YAML config: {e}")
            return {}

    def open(self) -> None:
        """Open WebSocket connections and start the event loop."""
        if self.is_connected:
            logger.warning("WebSocket is already connected")
            return
            
        logger.info("Opening Kraken WebSocket connection...")
        
        max_retries = 3
        retry_delay = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
                self.thread.start()
                
                timeout = 10
                start_time = time.time()
                while not self.is_connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                    
                if self.is_connected:
                    logger.info("Kraken WebSocket connected successfully")
                    return
                    
            except Exception as e:
                logger.warning(f"Connection attempt {retry_count + 1} failed: {e}")
                
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Retrying connection in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
        raise ConnectionError("Failed to establish WebSocket connection after multiple attempts")
    
    def close(self) -> None:
        """Close WebSocket connections and stop the event loop."""
        if not self.is_connected:
            logger.warning("WebSocket is not connected")
            return
            
        logger.info("Closing Kraken WebSocket connection...")
        self.is_running = False
        
        if self.loop and not self.loop.is_closed():
            try:
                future = asyncio.run_coroutine_threadsafe(self._close_connections(), self.loop)
                future.result(timeout=5)
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Error closing connections: {e}")
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        self.is_connected = False
        logger.info("Kraken WebSocket connection closed")
    
    def add_message_handler(self, message_type: str, handler: Callable) -> None:
        """Add a message handler for specific message types."""
        self.message_handlers[message_type].append(handler)
    
    def add_error_handler(self, handler: Callable) -> None:
        """Add an error handler callback."""
        self.error_handlers.append(handler)
    
    def send_message(self, message: dict, private: bool = False) -> None:
        """Send a message through the WebSocket."""
        if not self.is_connected:
            raise ConnectionError("WebSocket is not connected")
            
        ws = self.private_ws if private else self.public_ws
        if not ws:
            ws_type = "private" if private else "public"
            raise ConnectionError(f"{ws_type.capitalize()} WebSocket is not available")
            
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                ws.send(json.dumps(message)), 
                self.loop
            )

    def _run_event_loop(self) -> None:
        """Run the asyncio event loop in a separate thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            logger.error(f"Event loop error: {e}")
            self._handle_error(e)
        finally:
            try:
                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception as e:
                logger.warning(f"Error cleaning up tasks: {e}")
            finally:
                self.loop.close()
                logger.debug("Event loop closed")
    
    async def _connect_and_listen(self) -> None:
        """Establish WebSocket connections and listen for messages."""
        self.is_running = True
        
        try:
            self.public_ws = await websockets.connect(self.public_url)
            logger.info("Connected to public WebSocket")
            
            if self.api_key and self.api_secret:
                try:
                    self.private_ws = await websockets.connect(self.private_url)
                    logger.info("Connected to private WebSocket")
                except Exception as e:
                    logger.warning(f"Could not connect to private WebSocket: {e}")
            
            self.is_connected = True
            await self._listen_for_messages()
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.is_connected = False
            self._handle_error(e)
    
    async def _listen_for_messages(self) -> None:
        """Listen for incoming WebSocket messages."""
        tasks = []
        
        if self.public_ws:
            tasks.append(asyncio.create_task(self._listen_to_websocket(self.public_ws, "public")))
        if self.private_ws:
            tasks.append(asyncio.create_task(self._listen_to_websocket(self.private_ws, "private")))
        
        if not tasks:
            logger.error("No WebSocket connections available")
            return
            
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
        except Exception as e:
            logger.error(f"Error in message listening: {e}")
            self._handle_error(e)
    
    async def _listen_to_websocket(self, ws, ws_type: str) -> None:
        """Listen for messages from a specific WebSocket connection."""
        try:
            while self.is_running and ws:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    await self._handle_message(message)
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"{ws_type.capitalize()} WebSocket connection closed")
                    break
        except Exception as e:
            logger.error(f"Error listening to {ws_type} WebSocket: {e}")
            self._handle_error(e)
    
    async def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            
            if isinstance(data, dict):
                if 'event' in data:
                    await self._handle_system_event(data)
                elif 'errorMessage' in data:
                    logger.error(f"Kraken error: {data['errorMessage']}")
                    self._handle_error(Exception(data['errorMessage']))
            elif isinstance(data, list) and len(data) >= 4:
                await self._handle_market_data(data)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self._handle_error(e)
    
    async def _handle_system_event(self, data: dict) -> None:
        """Handle system events from Kraken."""
        event = data.get('event')
        
        if event == 'heartbeat':
            logger.debug("Received heartbeat")
        elif event == 'systemStatus':
            logger.info(f"System status: {data.get('status')}")
        elif event == 'subscriptionStatus':
            logger.info(f"Subscription status: {data}")
        elif event in ['addOrderStatus', 'cancelOrderStatus', 'editOrderStatus']:
            event_key = f"{event}_{data.get('reqid', 'default')}"
            if event_key in self.pending_responses:
                self.pending_responses[event_key] = data
                if event_key in self.response_events:
                    self.response_events[event_key].set()
            
        event_type = event if event else 'system'
        if event_type in self.message_handlers:
            for handler in self.message_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in {event_type} handler: {e}")

    async def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            
            if isinstance(data, dict):
                if 'event' in data:
                    await self._handle_system_event(data)
                elif 'errorMessage' in data:
                    logger.error(f"Kraken error: {data['errorMessage']}")
                    self._handle_error(Exception(data['errorMessage']))
            elif isinstance(data, list):
                # Market data updates
                await self._handle_market_data(data)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self._handle_error(e)

    async def _handle_market_data(self, data: list) -> None:
        """Handle market data updates."""
        try:
            # Different message formats:
            # 1. For book updates: [channelID, {data}, "channelName", "pair"]
            # 2. For other updates: [channelID, data, "channelName", "pair"]
            
            if len(data) < 2:
                return
                
            channel_id = data[0]
            market_data = data[1]
            
            # Get channel name and pair if available
            channel_name = data[2] if len(data) > 2 else None
            pair = data[3] if len(data) > 3 else None
            
            # Update internal data stores
            if channel_name and 'book' in channel_name:
                self._update_orderbook(pair, market_data, channel_name)
            elif channel_name and 'ticker' in channel_name:
                self.tickers[pair] = market_data
            
            # Route to handlers
            if channel_name and channel_name in self.message_handlers:
                for handler in self.message_handlers[channel_name]:
                    try:
                        handler(pair, market_data)
                    except Exception as e:
                        logger.error(f"Error in {channel_name} handler: {e}")
                        
        except Exception as e:
            logger.error(f"Error handling market data: {e}")
            self._handle_error(e)
    
    async def _handle_market_data(self, data: list) -> None:
        """Handle market data updates."""
        try:
            channel_id = data[0]
            market_data = data[1]
            channel_name = data[2]
            pair = data[3] if len(data) > 3 else None
            
            # Update internal data stores
            if 'book' in channel_name:
                self._update_orderbook(pair, market_data, channel_name)
            elif 'ticker' in channel_name:
                self.tickers[pair] = market_data
            
            # Route to handlers
            if channel_name in self.message_handlers:
                for handler in self.message_handlers[channel_name]:
                    handler(pair, market_data)
                    
        except Exception as e:
            logger.error(f"Error handling market data: {e}")
    
    def _update_orderbook(self, pair: str, data: dict, channel_name: str) -> None:
        """Update internal orderbook storage."""
        if pair not in self.orderbooks:
            self.orderbooks[pair] = {'asks': [], 'bids': []}
        
        if 'as' in data:  # Snapshot of asks
            self.orderbooks[pair]['asks'] = [
                (float(price), float(volume), float(timestamp))
                for price, volume, timestamp in data['as']
            ]
        elif 'a' in data:  # Ask update
            self._process_book_update(self.orderbooks[pair]['asks'], data['a'])
            
        if 'bs' in data:  # Snapshot of bids
            self.orderbooks[pair]['bids'] = [
                (float(price), float(volume), float(timestamp))
                for price, volume, timestamp in data['bs']
            ]
        elif 'b' in data:  # Bid update
            self._process_book_update(self.orderbooks[pair]['bids'], data['b'])
    
    def _process_book_update(self, book_side: list, updates: list) -> None:
        """Process order book updates."""
        for update in updates:
            price, volume, timestamp = update
            price = float(price)
            volume = float(volume)
            timestamp = float(timestamp)
            
            # Find and update existing price level
            found = False
            for i, (p, v, t) in enumerate(book_side):
                if p == price:
                    if volume == 0:
                        del book_side[i]
                    else:
                        book_side[i] = (price, volume, timestamp)
                    found = True
                    break
            
            # Add new price level if not found and volume > 0
            if not found and volume > 0:
                book_side.append((price, volume, timestamp))
                book_side.sort(reverse=(book_side is self.orderbooks[pair]['bids']))
    
    async def _close_connections(self) -> None:
        """Close WebSocket connections."""
        close_tasks = []
        if self.public_ws:
            close_tasks.append(self.public_ws.close())
        if self.private_ws:
            close_tasks.append(self.private_ws.close())
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
    
    def _handle_error(self, error: Exception) -> None:
        """Handle errors by calling registered error handlers."""
        for handler in self.error_handlers:
            try:
                handler(error)
            except Exception as e:
                logger.error(f"Error in error handler: {e}")
    
    def get_orderbook(self, pair: str) -> Optional[OrderBookSnapshot]:
        """Get the current orderbook snapshot for a pair."""
        if pair not in self.orderbooks:
            return None
        return OrderBookSnapshot(
            asks=self.orderbooks[pair]['asks'],
            bids=self.orderbooks[pair]['bids'],
            pair=pair,
            timestamp=time.time()
        )
    
    def get_ticker(self, pair: str) -> Optional[dict]:
        """Get the current ticker data for a pair."""
        return self.tickers.get(pair)
    
    def wait_for_response(self, event_type: str, timeout: float = 10.0, reqid: str = None) -> Dict[str, Any]:
        """
        Wait for a specific event response from the WebSocket.
        """
        if not self.is_connected:
            raise ConnectionError("WebSocket is not connected")
            
        event_key = f"{event_type}_{reqid or 'default'}"
        self.response_events[event_key] = threading.Event()
        self.pending_responses[event_key] = None
        
        try:
            if not self.response_events[event_key].wait(timeout):
                raise TimeoutError(f"Timeout waiting for {event_type} response")
                
            response = self.pending_responses[event_key]
            if response is None:
                raise RuntimeError(f"No response data received for {event_type}")
                
            return response
            
        finally:
            self.response_events.pop(event_key, None)
            self.pending_responses.pop(event_key, None)

    @property
    def connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.is_connected