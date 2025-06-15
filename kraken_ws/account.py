from typing import List, Optional, Dict, Any, Tuple
import logging
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from .kraken_ws import KrakenWebSocket
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Order:
    txid: str
    pair: str
    side: str
    type: str
    volume: float
    price: Optional[float] = None
    status: str = 'pending'
    timestamp: float = time.time()

class KrakenAuth:
    """Helper class for Kraken API authentication."""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_token = None
        self.token_expiry = None
        
    def get_kraken_signature(self, url_path: str, data: Dict[str, Any], secret: str) -> str:
        post_data = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + post_data).encode()
        message = url_path.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        return base64.b64encode(mac.digest()).decode()
        
    def get_websocket_token(self, base_url: str = "https://api.kraken.com") -> str:
        if self.ws_token and self.token_expiry and time.time() < self.token_expiry - 60:
            return self.ws_token
            
        url_path = "/0/private/GetWebSocketsToken"
        url = base_url + url_path
        data = {'nonce': str(int(1000 * time.time()))}
        signature = self.get_kraken_signature(url_path, data, self.api_secret)
        
        headers = {
            'API-Key': self.api_key,
            'API-Sign': signature,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('error'):
                raise Exception(f"Kraken API Error: {result['error']}")
                
            self.ws_token = result['result']['token']
            self.token_expiry = time.time() + (10 * 60)
            logger.info("Successfully retrieved WebSocket authentication token")
            return self.ws_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retrieve WebSocket token: {e}")
        except KeyError as e:
            raise Exception(f"Invalid response format: {e}")

class OrderManager:
    """Helper class for managing orders through the Kraken WebSocket API."""
    
    def __init__(self, account: 'KrakenAccount'):
        self.account = account
        self.orders = {}
        
    def add_order(self, pair: str, order_type: str, side: str, volume: str, price: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Add a new order."""
        return self.account.add_order(pair, side, order_type, volume, price, **kwargs)
        
    def cancel_order(self, txid: str) -> bool:
        """Cancel an existing order."""
        return self.account.cancel_order(txid)
        
    def edit_order(self, txid: str, pair: str, volume: str, price: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Edit an existing order."""
        return self.account.edit_order(txid, pair, volume, price, **kwargs)

class KrakenAccount:
    """Kraken WebSocket client for account operations."""
    
    def __init__(self, client: KrakenWebSocket):
        self.client = client
        self.auth = KrakenAuth(client.api_key, client.api_secret) if client.api_key and client.api_secret else None
        self.orders = OrderManager(self)
        
    def _get_authenticated_message(self, base_message: Dict[str, Any]) -> Dict[str, Any]:
        """Add authentication token to message."""
        if not self.auth:
            raise PermissionError("Account operations require API credentials")
        token = self.auth.get_websocket_token()
        message = base_message.copy()
        message['token'] = token
        return message
    
    def add_order(self, pair: str, side: str, order_type: str, volume: str, price: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Add a new order."""
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        if side.lower() not in ['buy', 'sell']:
            raise ValueError("Side must be 'buy' or 'sell'")
            
        valid_order_types = ['market', 'limit', 'stop-loss', 'stop-loss-limit', 
                           'take-profit', 'take-profit-limit', 'trailing-stop', 
                           'trailing-stop-limit', 'settle-position']
        if order_type.lower() not in valid_order_types:
            raise ValueError(f"Order type must be one of: {valid_order_types}")
            
        if order_type.lower() in ['limit', 'stop-loss-limit', 'take-profit-limit', 'trailing-stop-limit'] and not price:
            raise ValueError(f"Price is required for {order_type} orders")
            
        order = {
            "event": "addOrder",
            "pair": pair,
            "type": side.lower(),
            "ordertype": order_type.lower(),
            "volume": volume
        }
        
        if price:
            order["price"] = price
            
        for key, value in kwargs.items():
            if value is not None:
                order[key] = value
                
        authenticated_order = self._get_authenticated_message(order)
        self.client.send_message(authenticated_order, private=True)
        logger.info(f"Added {order_type} {side} order for {volume} {pair}")
        
        try:
            response = self.client.wait_for_response("addOrderStatus")
            return self._parse_add_order_response(response)
        except Exception as e:
            logger.error(f"Error waiting for add order response: {e}")
            return {"error": str(e)}
        
    def cancel_order(self, txid: str) -> bool:
        """Cancel an existing order."""
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        cancel = {
            "event": "cancelOrder",
            "txid": [txid]
        }
        
        authenticated_cancel = self._get_authenticated_message(cancel)
        self.client.send_message(authenticated_cancel, private=True)
        logger.info(f"Cancelled order {txid}")
        
        try:
            response = self.client.wait_for_response("cancelOrderStatus")
            return response.get("status") == "ok"
        except Exception as e:
            logger.error(f"Error waiting for cancel order response: {e}")
            return False
        
    def edit_order(self, txid: str, pair: str, volume: str, price: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Edit an existing order."""
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        edit = {
            "event": "editOrder",
            "orderid": txid,
            "pair": pair,
            "volume": volume
        }
        
        if price:
            edit["price"] = price
            
        for key, value in kwargs.items():
            if value is not None:
                edit[key] = value
                
        authenticated_edit = self._get_authenticated_message(edit)
        self.client.send_message(authenticated_edit, private=True)
        logger.info(f"Edited order {txid}")
        
        try:
            response = self.client.wait_for_response("editOrderStatus")
            return self._parse_edit_order_response(response)
        except Exception as e:
            logger.error(f"Error waiting for edit order response: {e}")
            return {"error": str(e)}
        
    def get_open_orders(self) -> Dict[str, Any]:
        """Get all open orders using REST API."""
        try:
            url = "https://api.kraken.com/0/private/OpenOrders"
            nonce = str(int(1000*time.time()))
            data = {"nonce": nonce}
            
            headers = {
                'API-Key': self.auth.api_key,
                'API-Sign': self.auth.get_kraken_signature("/0/private/OpenOrders", data, self.auth.api_secret),
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting open orders via REST: {e}")
            raise Exception(f"Failed to get open orders: {e}")

    def get_balances(self) -> Dict[str, str]:
        """Get account balances using REST API."""
        try:
            url = "https://api.kraken.com/0/private/Balance"
            nonce = str(int(1000*time.time()))
            data = {"nonce": nonce}
            
            headers = {
                'API-Key': self.auth.api_key,
                'API-Sign': self.auth.get_kraken_signature("/0/private/Balance", data, self.auth.api_secret),
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            return response.json().get('result', {})
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            raise Exception(f"Failed to get balances: {e}")
        
    def subscribe_to_private_feed(self, subscription_name: str, **kwargs) -> None:
        """Subscribe to a private WebSocket feed."""
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        subscription = {
            "event": "subscribe",
            "subscription": {
                "name": subscription_name
            }
        }
        
        for key, value in kwargs.items():
            subscription["subscription"][key] = value
            
        token = self.auth.get_websocket_token()
        subscription["subscription"]["token"] = token
        
        self.client.send_message(subscription, private=True)
        logger.info(f"Subscribed to private feed: {subscription_name}")
    
    def _parse_add_order_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'txid': response.get('txid'),
            'status': response.get('status', 'unknown'),
            'description': response.get('descr', ''),
            'error_message': response.get('errorMessage', ''),
            'event': response.get('event', ''),
            'reqid': response.get('reqid')
        }

    def _parse_edit_order_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'txid': response.get('txid'),
            'original_txid': response.get('originaltxid'),
            'status': response.get('status', 'unknown'),
            'description': response.get('descr', ''),
            'error_message': response.get('errorMessage', ''),
            'event': response.get('event', ''),
            'reqid': response.get('reqid')
        }

# Parsing functions
def parse_own_trades(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse own trades data into a standardized format.
    
    Args:
        data: Raw trades data from WebSocket
        
    Returns:
        List of parsed trade dictionaries
    """
    return [{
        'price': float(trade['price']),
        'volume': float(trade['vol']),
        'time': trade['time'],
        'type': trade['type'],
        'ordertype': trade['ordertype'],
        'misc': trade['misc']
    } for trade in data]

def parse_open_orders(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse open orders data into a standardized format.
    
    Args:
        data: Raw open orders data from WebSocket
        
    Returns:
        List of parsed order dictionaries
    """
    orders = []
    for txid, order in data.items():
        orders.append({
            'txid': txid,
            'refid': order.get('refid'),
            'userref': order.get('userref'),
            'status': order.get('status'),
            'opentm': float(order.get('opentm', 0)),
            'starttm': float(order.get('starttm', 0)),
            'expiretm': float(order.get('expiretm', 0)),
            'descr': {
                'pair': order['descr']['pair'],
                'type': order['descr']['type'],
                'ordertype': order['descr']['ordertype'],
                'price': order['descr']['price'],
                'price2': order['descr']['price2'],
                'leverage': order['descr']['leverage'],
                'order': order['descr']['order'],
                'close': order['descr'].get('close')
            },
            'vol': float(order.get('vol', 0)),
            'vol_exec': float(order.get('vol_exec', 0)),
            'cost': float(order.get('cost', 0)),
            'fee': float(order.get('fee', 0)),
            'price': float(order.get('price', 0)),
            'stopprice': float(order.get('stopprice', 0)),
            'limitprice': float(order.get('limitprice', 0)),
            'misc': order.get('misc', ''),
            'oflags': order.get('oflags', ''),
            'reason': order.get('reason')
        })
    return orders

def parse_balances(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Parse balances response data into a standardized format.
    
    Args:
        data: Raw balances response from WebSocket
        
    Returns:
        Dictionary of asset balances with float values
    """
    return {
        asset: float(balance)
        for asset, balance in data.items()
    }