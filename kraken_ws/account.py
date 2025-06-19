import asyncio
import aiohttp
import hashlib
import hmac
import base64
import time
import urllib.parse
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class KrakenAccount:
    """
    Kraken account management and trading operations.
    Handles REST API calls for account info, orders, and trades.
    """
    
    API_URL = "https://api.kraken.com"
    API_VERSION = "0"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = None
        self.api_secret = None
        self._load_credentials(api_key, api_secret)
        self.session = None
    
    def _load_credentials(self, api_key: Optional[str], api_secret: Optional[str]):
        """Load API credentials from config file or parameters."""
        current_file = Path(__file__)
        config_path = current_file.parent.parent / "config" / "config.yaml"
        config = self._load_config(config_path)
        
        self.api_key = api_key or config.get('kraken', {}).get('api_key')
        self.api_secret = api_secret or config.get('kraken', {}).get('api_secret')
        
        if not self.api_key or not self.api_secret:
            logger.warning("API credentials not found. Account operations will not be available.")
    
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
    
    def _get_kraken_signature(self, urlpath: str, data: Dict, secret: str) -> str:
        """Generate Kraken API signature."""
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                           is_private: bool = False) -> Dict:
        """Make HTTP request to Kraken API."""
        if is_private and (not self.api_key or not self.api_secret):
            raise ValueError("API credentials required for private endpoints")
        
        session = await self._get_session()
        url = f"{self.API_URL}/{self.API_VERSION}/{endpoint}"
        
        headers = {'User-Agent': 'Kraken WebSocket Client'}
        
        if is_private:
            if not data:
                data = {}
            data['nonce'] = str(int(1000 * time.time()))
            
            urlpath = f"/{self.API_VERSION}/{endpoint}"
            signature = self._get_kraken_signature(urlpath, data, self.api_secret)
            
            headers.update({
                'API-Key': self.api_key,
                'API-Sign': signature
            })
        
        try:
            if method.upper() == 'GET':
                async with session.get(url, headers=headers, params=data) as response:
                    result = await response.json()
            else:
                async with session.post(url, headers=headers, data=data) as response:
                    result = await response.json()
            
            if result.get('error'):
                raise Exception(f"API Error: {result['error']}")
            
            return result.get('result', {})
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    # Account Information Methods
    async def get_account_balance(self) -> Dict[str, str]:
        """Get account balance."""
        return await self._make_request('POST', 'private/Balance', is_private=True)
    
    async def get_trade_balance(self, asset: str = 'ZUSD') -> Dict:
        """Get trade balance info."""
        data = {'asset': asset}
        return await self._make_request('POST', 'private/TradeBalance', data, is_private=True)
    
    async def get_open_orders(self, trades: bool = False) -> Dict:
        """Get open orders."""
        data = {'trades': trades}
        return await self._make_request('POST', 'private/OpenOrders', data, is_private=True)
    
    async def get_closed_orders(self, trades: bool = False, userref: Optional[int] = None,
                               start: Optional[int] = None, end: Optional[int] = None,
                               ofs: Optional[int] = None, closetime: str = 'both') -> Dict:
        """Get closed orders."""
        data = {
            'trades': trades,
            'closetime': closetime
        }
        if userref is not None:
            data['userref'] = userref
        if start is not None:
            data['start'] = start
        if end is not None:
            data['end'] = end
        if ofs is not None:
            data['ofs'] = ofs
            
        return await self._make_request('POST', 'private/ClosedOrders', data, is_private=True)
    
    async def get_orders_info(self, txid: List[str], trades: bool = False) -> Dict:
        """Get orders info."""
        data = {
            'txid': ','.join(txid),
            'trades': trades
        }
        return await self._make_request('POST', 'private/QueryOrders', data, is_private=True)
    
    async def get_trades_history(self, type: str = 'all', trades: bool = False,
                                start: Optional[int] = None, end: Optional[int] = None,
                                ofs: Optional[int] = None) -> Dict:
        """Get trades history."""
        data = {
            'type': type,
            'trades': trades
        }
        if start is not None:
            data['start'] = start
        if end is not None:
            data['end'] = end
        if ofs is not None:
            data['ofs'] = ofs
            
        return await self._make_request('POST', 'private/TradesHistory', data, is_private=True)
    
    async def get_trades_info(self, txid: List[str], trades: bool = False) -> Dict:
        """Get trades info."""
        data = {
            'txid': ','.join(txid),
            'trades': trades
        }
        return await self._make_request('POST', 'private/QueryTrades', data, is_private=True)
    
    async def get_open_positions(self, txid: Optional[List[str]] = None,
                                docalcs: bool = False) -> Dict:
        """Get open positions."""
        data = {'docalcs': docalcs}
        if txid:
            data['txid'] = ','.join(txid)
            
        return await self._make_request('POST', 'private/OpenPositions', data, is_private=True)
    
    async def get_ledgers_info(self, asset: Optional[str] = None, aclass: str = 'currency',
                              type: str = 'all', start: Optional[int] = None,
                              end: Optional[int] = None, ofs: Optional[int] = None) -> Dict:
        """Get ledgers info."""
        data = {
            'aclass': aclass,
            'type': type
        }
        if asset:
            data['asset'] = asset
        if start is not None:
            data['start'] = start
        if end is not None:
            data['end'] = end
        if ofs is not None:
            data['ofs'] = ofs
            
        return await self._make_request('POST', 'private/Ledgers', data, is_private=True)
    
    # Trading Methods
    async def add_order(self, pair: str, type: str, ordertype: str, volume: str,
                       price: Optional[str] = None, price2: Optional[str] = None,
                       leverage: Optional[str] = None, oflags: Optional[str] = None,
                       starttm: Optional[str] = None, expiretm: Optional[str] = None,
                       userref: Optional[int] = None, validate: bool = False,
                       close_ordertype: Optional[str] = None, close_price: Optional[str] = None,
                       close_price2: Optional[str] = None, timeinforce: Optional[str] = None) -> Dict:
        """Add a new order."""
        data = {
            'pair': pair,
            'type': type,
            'ordertype': ordertype,
            'volume': volume,
            'validate': validate
        }
        
        # Add optional parameters
        if price is not None:
            data['price'] = price
        if price2 is not None:
            data['price2'] = price2
        if leverage is not None:
            data['leverage'] = leverage
        if oflags is not None:
            data['oflags'] = oflags
        if starttm is not None:
            data['starttm'] = starttm
        if expiretm is not None:
            data['expiretm'] = expiretm
        if userref is not None:
            data['userref'] = userref
        if close_ordertype is not None:
            data['close[ordertype]'] = close_ordertype
        if close_price is not None:
            data['close[price]'] = close_price
        if close_price2 is not None:
            data['close[price2]'] = close_price2
        if timeinforce is not None:
            data['timeinforce'] = timeinforce
        
        return await self._make_request('POST', 'private/AddOrder', data, is_private=True)
    
    async def cancel_order(self, txid: str) -> Dict:
        """Cancel an order."""
        data = {'txid': txid}
        return await self._make_request('POST', 'private/CancelOrder', data, is_private=True)
    
    async def cancel_all_orders(self) -> Dict:
        """Cancel all open orders."""
        return await self._make_request('POST', 'private/CancelAll', is_private=True)
    
    async def cancel_all_orders_after(self, timeout: int) -> Dict:
        """Cancel all orders after X seconds."""
        data = {'timeout': timeout}
        return await self._make_request('POST', 'private/CancelAllOrdersAfter', data, is_private=True)
    
    # Convenience Methods
    async def buy_market_order(self, pair: str, volume: str, validate: bool = False) -> Dict:
        """Place a market buy order."""
        return await self.add_order(
            pair=pair,
            type='buy',
            ordertype='market',
            volume=volume,
            validate=validate
        )
    
    async def sell_market_order(self, pair: str, volume: str, validate: bool = False) -> Dict:
        """Place a market sell order."""
        return await self.add_order(
            pair=pair,
            type='sell',
            ordertype='market',
            volume=volume,
            validate=validate
        )
    
    async def buy_limit_order(self, pair: str, volume: str, price: str, validate: bool = False) -> Dict:
        """Place a limit buy order."""
        return await self.add_order(
            pair=pair,
            type='buy',
            ordertype='limit',
            volume=volume,
            price=price,
            validate=validate
        )
    
    async def sell_limit_order(self, pair: str, volume: str, price: str, validate: bool = False) -> Dict:
        """Place a limit sell order."""
        return await self.add_order(
            pair=pair,
            type='sell',
            ordertype='limit',
            volume=volume,
            price=price,
            validate=validate
        )
    
    async def get_portfolio_value(self, base_currency: str = 'USD') -> Dict[str, float]:
        """Calculate total portfolio value in base currency."""
        try:
            balance = await self.get_account_balance()
            
            # For simplicity, this is a basic implementation
            # In practice, you'd want to fetch current prices and convert everything
            portfolio = {}
            total_value = 0.0
            
            for asset, amount in balance.items():
                amount_float = float(amount)
                if amount_float > 0:
                    portfolio[asset] = amount_float
                    
                    # Add value calculation logic here
                    # You'd need to fetch current prices from markets.py
                    
            return portfolio
            
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            return {}
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()