import asyncio
import aiohttp
import hashlib
import hmac
import base64
import time
import urllib.parse
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import yaml
import websockets

logger = logging.getLogger(__name__)

class KrakenAccount:
    """
    Manages trading operations for a Kraken account using a persistent WebSocket connection.
    This client is designed for real-time order management.
    """
    
    API_URL = "https://api.kraken.com"
    WS_URL = "wss://ws-auth.kraken.com"
    API_VERSION = "0"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initializes the KrakenAccount, loading credentials but not connecting."""
        self.api_key = None
        self.api_secret = None
        self._load_credentials(api_key, api_secret)
        
        self._session = None
        self._ws_connection = None
        self._ws_authenticated = False
        self._auth_token = None
        
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._message_handler_task: Optional[asyncio.Task] = None
        self._connection_lock = asyncio.Lock()

    @classmethod
    async def create(cls, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Factory method to create and connect a KrakenAccount instance."""
        account = cls(api_key, api_secret)
        await account.connect()
        return account

    def _load_credentials(self, api_key: Optional[str], api_secret: Optional[str]):
        """Loads API credentials from a config file or from provided parameters."""
        current_file = Path(__file__)
        config_path = current_file.parent.parent / "config" / "config.yaml"
        config = self._load_config(config_path)
        
        self.api_key = api_key or config.get('kraken', {}).get('api_key')
        self.api_secret = api_secret or config.get('kraken', {}).get('api_secret')
        
        if not self.api_key or not self.api_secret:
            logger.error("API key and secret are required for account operations.")
            raise ValueError("API key and secret not found.")
    
    def _load_config(self, config_path: Path) -> Dict:
        """Loads configuration from a specified YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Configuration file not found at {config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config: {e}")
            return {}
            
    def _get_ws_auth_token_signature(self, data: Dict) -> str:
        """Generates the signature for the WebSocket authentication token."""
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = b'/0/private/GetWebSocketsToken' + hashlib.sha256(encoded).digest()
        
        mac = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    async def _get_ws_auth_token(self) -> str:
        """Retrieves a WebSocket authentication token from the Kraken REST API."""
        if not self._session:
            self._session = aiohttp.ClientSession()

        data = {'nonce': str(int(1000 * time.time()))}
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._get_ws_auth_token_signature(data)
        }
        
        url = f"{self.API_URL}/{self.API_VERSION}/private/GetWebSocketsToken"
        
        async with self._session.post(url, headers=headers, data=data) as response:
            result = await response.json()
            
        if result.get('error'):
            raise Exception(f"Failed to get WebSocket token: {result['error']}")
            
        return result['result']['token']

    async def connect(self):
        """Establishes and authenticates the WebSocket connection."""
        async with self._connection_lock:
            if self._ws_connection and self._ws_connection.open:
                logger.info("WebSocket connection already established.")
                return

            try:
                self._auth_token = await self._get_ws_auth_token()
                
                self._ws_connection = await websockets.connect(
                    self.WS_URL,
                    ping_interval=20,
                    ping_timeout=10
                )
                
                self._ws_authenticated = True
                
                if self._message_handler_task:
                    self._message_handler_task.cancel()
                    
                self._message_handler_task = asyncio.create_task(self._handle_ws_messages())
                logger.info("WebSocket connection established and authenticated.")

            except Exception as e:
                logger.error(f"Failed to establish WebSocket connection: {e}")
                self._ws_authenticated = False
                if self._ws_connection:
                    await self._ws_connection.close()
                raise

    async def _handle_ws_messages(self):
        """Continuously listens for and processes incoming WebSocket messages."""
        try:
            # Use `async for` to robustly iterate over messages and handle connection closing.
            async for message in self._ws_connection:
                try:
                    data = json.loads(message)
                    logger.debug(f"WS Recv: {data}")

                    if isinstance(data, dict) and "reqid" in data:
                        reqid = data.get("reqid")
                        if reqid in self._pending_requests:
                            future = self._pending_requests.pop(reqid)
                            if data.get("status") == "error":
                                future.set_exception(Exception(f"Kraken API Error: {data.get('errorMessage', 'Unknown error')}"))
                            else:
                                future.set_result(data)
                    
                    elif isinstance(data, dict) and data.get("method") == "ping":
                        # Respond to server-initiated pings
                        pong_message = {"method": "pong", "req_id": data.get("req_id")}
                        await self._ws_connection.send(json.dumps(pong_message))

                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode WebSocket message: {message}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed.")
        except Exception as e:
            logger.error(f"Error in WebSocket message handler: {e}", exc_info=True)
        finally:
            self._ws_authenticated = False
            # Clean up any pending requests that will never resolve
            for future in self._pending_requests.values():
                if not future.done():
                    future.set_exception(Exception("WebSocket connection lost."))
            self._pending_requests.clear()

    async def _send_request(self, payload: Dict, timeout: float = 10.0) -> Dict:
        """Sends a request over the WebSocket and waits for a response."""
        if not self._ws_authenticated or not self._ws_connection:
            raise ConnectionError("WebSocket is not connected. Call connect() first.")

        reqid = int(time.time() * 1000)
        payload["reqid"] = reqid
        payload["token"] = self._auth_token

        future = asyncio.get_running_loop().create_future()
        self._pending_requests[reqid] = future
        
        await self._ws_connection.send(json.dumps(payload))
        logger.debug(f"WS Sent: {payload}")
        
        return await asyncio.wait_for(future, timeout=timeout)

    # --- Public Trading Methods ---

    async def add_order(self, pair: str, type: str, ordertype: str, volume: str,
                       price: Optional[str] = None, validate: bool = False, **kwargs) -> Dict:
        """Places a new order via WebSocket."""
        payload = {
            "event": "addOrder",
            "pair": pair,
            "type": type,
            "ordertype": ordertype,
            "volume": str(volume),
            "validate": str(validate).lower()
        }
        if price:
            payload["price"] = str(price)
        
        payload.update(kwargs)
        return await self._send_request(payload)

    async def edit_order(self, txid: str, volume: Optional[str] = None,
                     limit_price: Optional[str] = None, **kwargs) -> Dict:
        """Edits an existing order via WebSocket."""
        payload = {
            "event": "amendOrder",
            "txid": txid,
        }
        if volume:
            payload["volume"] = str(volume)
        if limit_price:
            payload["limit_price"] = str(limit_price)  # Changed from "price" to "limit_price"
        
        payload.update(kwargs)
        return await self._send_request(payload)

    async def cancel_order(self, txid: Union[str, List[str]]) -> Dict:
        """Cancels one or more open orders via WebSocket."""
        payload = {
            "event": "cancelOrder",
            "txid": [txid] if isinstance(txid, str) else txid
        }
        return await self._send_request(payload)

    async def cancel_all_orders(self) -> Dict:
        """Cancels all open orders via WebSocket."""
        payload = {"event": "cancelAll"}
        return await self._send_request(payload)

    async def close(self):
        """Closes the WebSocket connection and cleans up resources."""
        if self._message_handler_task:
            self._message_handler_task.cancel()
            try:
                await self._message_handler_task
            except asyncio.CancelledError:
                pass
        
        if self._ws_connection and self._ws_connection.open:
            await self._ws_connection.close()
            logger.info("WebSocket connection closed.")
        
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()