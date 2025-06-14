import asyncio
import json
import websockets
import threading
import time
from typing import Dict, List, Callable, Optional, Any
import logging

import yaml
import yaml
import os
from pathlib import Path


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KrakenWebSocket:
    """
    Core Kraken WebSocket API client for managing connections and message routing.
    
    This is the base class that handles WebSocket connections, message routing,
    and provides the foundation for market data and account operations.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Initialize the Kraken WebSocket client.
        
        Args:
            api_key: Kraken API key for authenticated operations
            api_secret: Kraken API secret for authenticated operations
        """
        # Get the path to the config file relative to this file's location
        current_file = Path(__file__)  # kraken_ws/kraken_ws.py
        config_path = current_file.parent.parent / "config" / "config.yaml"
        
        # Load configuration
        config = self._load_config(config_path)
        
        # Set API credentials from config
        self.api_key = config.get('kraken', {}).get('api_key')
        self.api_secret = config.get('kraken', {}).get('api_secret')
        
        # Validate that credentials were loaded
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret must be provided in config.yaml")

        
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
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.error_handlers: List[Callable] = []
        
        # Subscription tracking
        self.subscriptions = set()

    def _load_config(self, config_path):
        """Loads config from yaml path"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML config: {e}")

        
    def open(self) -> None:
        """Open WebSocket connections and start the event loop."""
        if self.is_connected:
            logger.warning("WebSocket is already connected")
            return
            
        logger.info("Opening Kraken WebSocket connection...")
        
        # Start the event loop in a separate thread
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        # Wait for connection to be established
        timeout = 10
        start_time = time.time()
        while not self.is_connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            
        if not self.is_connected:
            raise ConnectionError("Failed to establish WebSocket connection within timeout")
            
        logger.info("Kraken WebSocket connected successfully")
    
    def close(self) -> None:
        """Close WebSocket connections and stop the event loop."""
        if not self.is_connected:
            logger.warning("WebSocket is not connected")
            return
            
        logger.info("Closing Kraken WebSocket connection...")
        self.is_running = False
        
        # Close WebSocket connections
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._close_connections(), self.loop)
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        self.is_connected = False
        logger.info("Kraken WebSocket connection closed")
    
    def add_message_handler(self, message_type: str, handler: Callable) -> None:
        """
        Add a message handler for specific message types.
        
        Args:
            message_type: Type of message ('ticker', 'trade', 'ohlc', 'book', etc.)
            handler: Callback function to handle the message
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def add_error_handler(self, handler: Callable) -> None:
        """Add an error handler callback."""
        self.error_handlers.append(handler)
    
    def send_message(self, message: dict, private: bool = False) -> None:
        """
        Send a message through the WebSocket.
        
        Args:
            message: Message dictionary to send
            private: Whether to send through private (authenticated) WebSocket
        """
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
            self.loop.close()
    
    async def _connect_and_listen(self) -> None:
        """Establish WebSocket connections and listen for messages."""
        self.is_running = True
        
        try:
            # Connect to public WebSocket
            self.public_ws = await websockets.connect(self.public_url)
            self.is_connected = True
            
            # If we have credentials, also connect to private WebSocket
            if self.api_key and self.api_secret:
                # Note: Private WebSocket requires authentication token
                # This is a simplified version - full implementation would need proper auth
                logger.info("Private WebSocket authentication not fully implemented in this example")
            
            # Listen for messages
            await self._listen_for_messages()
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.is_connected = False
            self._handle_error(e)
    
    async def _listen_for_messages(self) -> None:
        """Listen for incoming WebSocket messages."""
        try:
            while self.is_running and self.public_ws:
                try:
                    message = await asyncio.wait_for(
                        self.public_ws.recv(), 
                        timeout=1.0
                    )
                    await self._handle_message(message)
                    
                except asyncio.TimeoutError:
                    # Timeout is normal, continue listening
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                    
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
            self._handle_error(e)
    
    async def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            
            # Handle different message types
            if isinstance(data, dict):
                if 'event' in data:
                    # System events (subscriptionStatus, heartbeat, etc.)
                    await self._handle_system_event(data)
                elif 'errorMessage' in data:
                    logger.error(f"Kraken error: {data['errorMessage']}")
                    self._handle_error(Exception(data['errorMessage']))
            elif isinstance(data, list) and len(data) >= 4:
                # Market data updates
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
        else:
            logger.debug(f"Received system event: {data}")
            
        # Route system events to handlers
        if 'system' in self.message_handlers:
            for handler in self.message_handlers['system']:
                handler(data)
    
    async def _handle_market_data(self, data: list) -> None:
        """Handle market data updates."""
        try:
            channel_id = data[0]
            market_data = data[1]
            channel_name = data[2]
            pair = data[3] if len(data) > 3 else None
            
            # Route to appropriate handlers based on channel name
            if 'ticker' in channel_name and 'ticker' in self.message_handlers:
                for handler in self.message_handlers['ticker']:
                    handler(pair, market_data)
            elif 'trade' in channel_name and 'trade' in self.message_handlers:
                for handler in self.message_handlers['trade']:
                    handler(pair, market_data)
            elif 'ohlc' in channel_name and 'ohlc' in self.message_handlers:
                for handler in self.message_handlers['ohlc']:
                    handler(pair, market_data)
            elif 'book' in channel_name and 'book' in self.message_handlers:
                for handler in self.message_handlers['book']:
                    handler(pair, market_data)
            elif 'spread' in channel_name and 'spread' in self.message_handlers:
                for handler in self.message_handlers['spread']:
                    handler(pair, market_data)
                    
        except Exception as e:
            logger.error(f"Error handling market data: {e}")
    
    async def _close_connections(self) -> None:
        """Close WebSocket connections."""
        if self.public_ws:
            await self.public_ws.close()
        if self.private_ws:
            await self.private_ws.close()
    
    def _handle_error(self, error: Exception) -> None:
        """Handle errors by calling registered error handlers."""
        for handler in self.error_handlers:
            try:
                handler(error)
            except Exception as e:
                logger.error(f"Error in error handler: {e}")
    
    @property
    def connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.is_connected
    
    def get_subscriptions(self) -> set:
        """Get the set of active subscriptions."""
        return self.subscriptions.copy()

    def wait_for_response(self, event_type: str, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Wait for a specific event response from the WebSocket.
        
        Args:
            event_type: Type of event to wait for (e.g., 'addOrder', 'cancelOrder')
            timeout: Maximum time to wait in seconds
            
        Returns:
            Response data dictionary
            
        Raises:
            TimeoutError: If no response is received within the timeout period
        """
        if not self.is_connected:
            raise ConnectionError("WebSocket is not connected")
            
        response_received = threading.Event()
        response_data = {}
        
        def response_handler(data: Dict[str, Any]) -> None:
            if data.get('event') == event_type:
                response_data.update(data)
                response_received.set()
        
        # Add temporary handler for this specific response
        self.add_message_handler(event_type, response_handler)
        
        try:
            # Wait for response with timeout
            if not response_received.wait(timeout):
                raise TimeoutError(f"Timeout waiting for {event_type} response")
                
            return response_data
            
        finally:
            # Remove the temporary handler
            if event_type in self.message_handlers:
                self.message_handlers[event_type].remove(response_handler)