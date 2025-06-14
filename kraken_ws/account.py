from typing import List, Optional, Dict, Any
import logging
from .kraken_ws import KrakenWebSocket

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Helper class for managing orders through the Kraken WebSocket API.
    """
    
    def __init__(self, account: 'KrakenAccount'):
        """
        Initialize the order manager.
        
        Args:
            account: KrakenAccount instance to use for order operations
        """
        self.account = account
        
    def add_order(self, pair: str, side: str, order_type: str, volume: str, price: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new order.
        
        Args:
            pair: Trading pair (e.g., 'BTC/USD')
            side: Order side ('buy' or 'sell')
            order_type: Order type ('market' or 'limit')
            volume: Order volume
            price: Optional price for limit orders
            
        Returns:
            Order response dictionary
        """
        return self.account.add_order(pair, side, order_type, volume, price)
        
    def cancel_order(self, txid: str) -> bool:
        """
        Cancel an existing order.
        
        Args:
            txid: Transaction ID of the order to cancel
            
        Returns:
            True if order was cancelled successfully
        """
        return self.account.cancel_order(txid)
        
    def edit_order(self, txid: str, pair: str, side: str, price: str, volume: str) -> Dict[str, Any]:
        """
        Edit an existing order.
        
        Args:
            txid: Transaction ID of the order to edit
            pair: Trading pair
            side: Order side ('buy' or 'sell')
            price: New price
            volume: New volume
            
        Returns:
            Updated order response dictionary
        """
        return self.account.edit_order(txid, pair, side, price, volume)


class KrakenAccount:
    """
    Kraken WebSocket client for account operations.
    
    Handles authenticated operations including:
    - Order management (add, cancel, edit)
    - Balance queries
    - Trade history
    """
    
    def __init__(self, client: KrakenWebSocket):
        """
        Initialize the account client.
        
        Args:
            client: KrakenWebSocket instance to use for communication
        """
        self.client = client
        
    def add_order(self, pair: str, side: str, order_type: str, volume: str, price: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new order.
        
        Args:
            pair: Trading pair (e.g., 'BTC/USD')
            side: Order side ('buy' or 'sell')
            order_type: Order type ('market' or 'limit')
            volume: Order volume
            price: Optional price for limit orders
            
        Returns:
            Order response dictionary
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        if side.lower() not in ['buy', 'sell']:
            raise ValueError("Side must be 'buy' or 'sell'")
            
        if order_type.lower() not in ['market', 'limit']:
            raise ValueError("Order type must be 'market' or 'limit'")
            
        if order_type.lower() == 'limit' and not price:
            raise ValueError("Price is required for limit orders")
            
        order = {
            "event": "addOrder",
            "pair": pair,
            "type": side.lower(),
            "ordertype": order_type.lower(),
            "volume": volume
        }
        
        if price:
            order["price"] = price
            
        self.client.send_message(order)
        logger.info(f"Added {order_type} {side} order for {volume} {pair}")
        
        # Wait for and return the response
        response = self.client.wait_for_response("addOrder")
        return parse_order_response(response)
        
    def cancel_order(self, txid: str) -> bool:
        """
        Cancel an existing order.
        
        Args:
            txid: Transaction ID of the order to cancel
            
        Returns:
            True if order was cancelled successfully
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        cancel = {
            "event": "cancelOrder",
            "txid": txid
        }
        
        self.client.send_message(cancel)
        logger.info(f"Cancelled order {txid}")
        
        # Wait for and return the response
        response = self.client.wait_for_response("cancelOrder")
        return response.get("status") == "success"
        
    def edit_order(self, txid: str, pair: str, side: str, price: str, volume: str) -> Dict[str, Any]:
        """
        Edit an existing order.
        
        Args:
            txid: Transaction ID of the order to edit
            pair: Trading pair
            side: Order side ('buy' or 'sell')
            price: New price
            volume: New volume
            
        Returns:
            Updated order response dictionary
        """
        if not self.client.connected:
            raise ConnectionError("WebSocket is not connected")
            
        if side.lower() not in ['buy', 'sell']:
            raise ValueError("Side must be 'buy' or 'sell'")
            
        edit = {
            "event": "editOrder",
            "txid": txid,
            "pair": pair,
            "type": side.lower(),
            "price": price,
            "volume": volume
        }
        
        self.client.send_message(edit)
        logger.info(f"Edited order {txid}")
        
        # Wait for and return the response
        response = self.client.wait_for_response("editOrder")
        return parse_order_response(response)


def parse_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse order response data into a standardized format.
    
    Args:
        response: Raw order response from WebSocket
        
    Returns:
        Parsed order response dictionary
    """
    return {
        'txid': response.get('txid', []),
        'status': response.get('status', 'unknown'),
        'description': response.get('descr', {}).get('order', ''),
        'error': response.get('error', [])
    }


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
