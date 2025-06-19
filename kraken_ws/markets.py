import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class KrakenMarkets:
    """
    Kraken market data and analysis tools.
    Handles public market data, price analysis, and trading utilities.
    """
    
    API_URL = "https://api.kraken.com"
    API_VERSION = "0"
    
    def __init__(self):
        self.session = None
        self._asset_pairs = {}
        self._assets = {}
        self._last_update = None
        
    async def _get_session(self):
        """Get or create aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Kraken public API."""
        session = await self._get_session()
        url = f"{self.API_URL}/{self.API_VERSION}/public/{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                result = await response.json()
            
            if result.get('error'):
                raise Exception(f"API Error: {result['error']}")
            
            return result.get('result', {})
            
        except Exception as e:
            logger.error(f"Market data request failed: {e}")
            raise
    
    # Asset and Pair Information
    async def get_server_time(self) -> Dict:
        """Get server time."""
        return await self._make_request('Time')
    
    async def get_system_status(self) -> Dict:
        """Get system status."""
        return await self._make_request('SystemStatus')
    
    async def get_assets(self, info: str = 'info', aclass: str = 'currency') -> Dict:
        """Get asset info."""
        params = {'info': info, 'aclass': aclass}
        result = await self._make_request('Assets', params)
        self._assets = result
        return result
    
    async def get_asset_pairs(self, info: str = 'info', pair: Optional[str] = None) -> Dict:
        """Get tradeable asset pairs."""
        params = {'info': info}
        if pair:
            params['pair'] = pair
        
        result = await self._make_request('AssetPairs', params)
        self._asset_pairs = result
        self._last_update = time.time()
        return result
    
    # Market Data
    async def get_ticker(self, pair: Union[str, List[str]]) -> Dict:
        """Get ticker information."""
        if isinstance(pair, list):
            pair = ','.join(pair)
        
        params = {'pair': pair}
        return await self._make_request('Ticker', params)
    
    async def get_ohlc(self, pair: str, interval: int = 1, since: Optional[int] = None) -> Dict:
        """Get OHLC data."""
        params = {'pair': pair, 'interval': interval}
        if since:
            params['since'] = since
        
        return await self._make_request('OHLC', params)
    
    async def get_order_book(self, pair: str, count: int = 100) -> Dict:
        """Get order book."""
        params = {'pair': pair, 'count': count}
        return await self._make_request('Depth', params)
    
    async def get_recent_trades(self, pair: str, since: Optional[int] = None) -> Dict:
        """Get recent trades."""
        params = {'pair': pair}
        if since:
            params['since'] = since
        
        return await self._make_request('Trades', params)
    
    async def get_recent_spread(self, pair: str, since: Optional[int] = None) -> Dict:
        """Get recent spread data."""
        params = {'pair': pair}
        if since:
            params['since'] = since
        
        return await self._make_request('Spread', params)
    
    # Price Analysis Methods
    async def get_price(self, pair: str) -> float:
        """Get current price for a pair."""
        try:
            ticker = await self.get_ticker(pair)
            pair_data = list(ticker.values())[0]
            return float(pair_data['c'][0])  # Last trade price
        except Exception as e:
            logger.error(f"Error getting price for {pair}: {e}")
            raise
    
    async def get_bid_ask(self, pair: str) -> Dict[str, float]:
        """Get current bid/ask prices."""
        try:
            ticker = await self.get_ticker(pair)
            pair_data = list(ticker.values())[0]
            return {
                'bid': float(pair_data['b'][0]),
                'ask': float(pair_data['a'][0]),
                'spread': float(pair_data['a'][0]) - float(pair_data['b'][0])
            }
        except Exception as e:
            logger.error(f"Error getting bid/ask for {pair}: {e}")
            raise
    
    async def get_24h_stats(self, pair: str) -> Dict[str, float]:
        """Get 24h trading statistics."""
        try:
            ticker = await self.get_ticker(pair)
            pair_data = list(ticker.values())[0]
            
            return {
                'price': float(pair_data['c'][0]),
                'volume': float(pair_data['v'][1]),  # 24h volume
                'volume_weighted_avg': float(pair_data['p'][1]),  # 24h volume weighted average
                'trades': int(pair_data['t'][1]),  # 24h number of trades
                'low': float(pair_data['l'][1]),  # 24h low
                'high': float(pair_data['h'][1]),  # 24h high
                'open': float(pair_data['o']),  # Today's opening price
            }
        except Exception as e:
            logger.error(f"Error getting 24h stats for {pair}: {e}")
            raise
    
    async def get_historical_data(self, pair: str, interval: int = 1440, 
                                 days: int = 30) -> List[Dict]:
        """Get historical OHLC data."""
        try:
            since = int(time.time()) - (days * 24 * 60 * 60)
            ohlc_data = await self.get_ohlc(pair, interval, since)
            
            pair_key = list(ohlc_data.keys())[0]
            raw_data = ohlc_data[pair_key]
            
            formatted_data = []
            for candle in raw_data:
                formatted_data.append({
                    'timestamp': int(candle[0]),
                    'datetime': datetime.fromtimestamp(candle[0]),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'vwap': float(candle[5]),
                    'volume': float(candle[6]),
                    'count': int(candle[7])
                })
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {pair}: {e}")
            raise
    
    # Trading Utilities
    async def get_minimum_order_size(self, pair: str) -> float:
        """Get minimum order size for a pair."""
        try:
            if not self._asset_pairs or time.time() - (self._last_update or 0) > 3600:
                await self.get_asset_pairs()
            
            if pair in self._asset_pairs:
                return float(self._asset_pairs[pair]['ordermin'])
            else:
                # Try to find pair with different formatting
                for p, info in self._asset_pairs.items():
                    if pair.replace('/', '') in p or pair.replace('/', '').upper() in p:
                        return float(info['ordermin'])
                
                raise ValueError(f"Pair {pair} not found")
                
        except Exception as e:
            logger.error(f"Error getting minimum order size for {pair}: {e}")
            raise
    
    async def get_lot_decimals(self, pair: str) -> int:
        """Get lot decimals for a pair."""
        try:
            if not self._asset_pairs or time.time() - (self._last_update or 0) > 3600:
                await self.get_asset_pairs()
            
            if pair in self._asset_pairs:
                return int(self._asset_pairs[pair]['lot_decimals'])
            else:
                # Try to find pair with different formatting
                for p, info in self._asset_pairs.items():
                    if pair.replace('/', '') in p or pair.replace('/', '').upper() in p:
                        return int(info['lot_decimals'])
                
                raise ValueError(f"Pair {pair} not found")
                
        except Exception as e:
            logger.error(f"Error getting lot decimals for {pair}: {e}")
            raise
    
    async def get_pair_decimals(self, pair: str) -> int:
        """Get pair decimals for a pair."""
        try:
            if not self._asset_pairs or time.time() - (self._last_update or 0) > 3600:
                await self.get_asset_pairs()
            
            if pair in self._asset_pairs:
                return int(self._asset_pairs[pair]['pair_decimals'])
            else:
                # Try to find pair with different formatting
                for p, info in self._asset_pairs.items():
                    if pair.replace('/', '') in p or pair.replace('/', '').upper() in p:
                        return int(info['pair_decimals'])
                
                raise ValueError(f"Pair {pair} not found")
                
        except Exception as e:
            logger.error(f"Error getting pair decimals for {pair}: {e}")
            raise
    
    def format_volume(self, volume: float, pair: str) -> str:
        """Format volume according to pair specifications."""
        try:
            # This would need lot_decimals from get_lot_decimals
            # For now, return a reasonable default
            return f"{volume:.8f}".rstrip('0').rstrip('.')
        except Exception as e:
            logger.error(f"Error formatting volume: {e}")
            return str(volume)
    
    def format_price(self, price: float, pair: str) -> str:
        """Format price according to pair specifications."""
        try:
            # This would need pair_decimals from get_pair_decimals
            # For now, return a reasonable default
            return f"{price:.5f}".rstrip('0').rstrip('.')
        except Exception as e:
            logger.error(f"Error formatting price: {e}")
            return str(price)
    
    # Analysis Methods
    async def calculate_sma(self, pair: str, period: int = 20, interval: int = 1440) -> float:
        """Calculate Simple Moving Average."""
        try:
            days = max(period + 5, 30)  # Get a bit more data than needed
            historical_data = await self.get_historical_data(pair, interval, days)
            
            if len(historical_data) < period:
                raise ValueError(f"Not enough data for SMA calculation. Need {period}, got {len(historical_data)}")
            
            recent_prices = [candle['close'] for candle in historical_data[-period:]]
            return sum(recent_prices) / len(recent_prices)
            
        except Exception as e:
            logger.error(f"Error calculating SMA for {pair}: {e}")
            raise
    
    async def calculate_ema(self, pair: str, period: int = 20, interval: int = 1440) -> float:
        """Calculate Exponential Moving Average."""
        try:
            days = max(period * 2, 50)  # Get more data for EMA
            historical_data = await self.get_historical_data(pair, interval, days)
            
            if len(historical_data) < period:
                raise ValueError(f"Not enough data for EMA calculation. Need {period}, got {len(historical_data)}")
            
            prices = [candle['close'] for candle in historical_data]
            
            # Calculate EMA
            multiplier = 2 / (period + 1)
            ema = prices[0]  # Start with first price
            
            for price in prices[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
            
        except Exception as e:
            logger.error(f"Error calculating EMA for {pair}: {e}")
            raise
    
    async def calculate_rsi(self, pair: str, period: int = 14, interval: int = 1440) -> float:
        """Calculate Relative Strength Index."""
        try:
            days = max(period + 10, 30)
            historical_data = await self.get_historical_data(pair, interval, days)
            
            if len(historical_data) < period + 1:
                raise ValueError(f"Not enough data for RSI calculation")
            
            prices = [candle['close'] for candle in historical_data]
            
            # Calculate price changes
            price_changes = []
            for i in range(1, len(prices)):
                price_changes.append(prices[i] - prices[i-1])
            
            # Separate gains and losses
            gains = [change if change > 0 else 0 for change in price_changes]
            losses = [-change if change < 0 else 0 for change in price_changes]
            
            # Calculate average gain and loss
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100.0  # Avoid division by zero
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI for {pair}: {e}")
            raise
    
    async def get_volatility(self, pair: str, period: int = 20, interval: int = 1440) -> float:
        """Calculate price volatility (standard deviation of returns)."""
        try:
            days = max(period + 5, 30)
            historical_data = await self.get_historical_data(pair, interval, days)
            
            if len(historical_data) < period:
                raise ValueError(f"Not enough data for volatility calculation")
            
            prices = [candle['close'] for candle in historical_data[-period:]]
            
            # Calculate returns
            returns = []
            for i in range(1, len(prices)):
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            # Calculate standard deviation
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatility = variance ** 0.5
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility for {pair}: {e}")
            raise
    
    # Utility Methods
    async def find_pair(self, asset1: str, asset2: str) -> Optional[str]:
        """Find the correct pair name for two assets."""
        try:
            if not self._asset_pairs:
                await self.get_asset_pairs()
            
            # Try different combinations
            possible_pairs = [
                f"{asset1}{asset2}",
                f"{asset2}{asset1}",
                f"{asset1.upper()}{asset2.upper()}",
                f"{asset2.upper()}{asset1.upper()}",
                f"X{asset1}Z{asset2}",
                f"X{asset2}Z{asset1}",
            ]
            
            for pair in possible_pairs:
                if pair in self._asset_pairs:
                    return pair
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding pair for {asset1}/{asset2}: {e}")
            return None
    
    async def get_all_pairs(self) -> List[str]:
        """Get list of all available trading pairs."""
        try:
            if not self._asset_pairs:
                await self.get_asset_pairs()
            
            return list(self._asset_pairs.keys())
            
        except Exception as e:
            logger.error(f"Error getting all pairs: {e}")
            return []
    
    async def get_popular_pairs(self) -> List[str]:
        """Get list of popular trading pairs."""
        popular = [
            'XXBTZUSD', 'XETHZUSD', 'ADAUSD', 'SOLUSD', 'DOTUSD',
            'LINKUSD', 'UNIUSD', 'LTCUSD', 'BCHUSD', 'XRPUSD',
            'ATOMUSD', 'ALGOUSD', 'MATICUSD', 'AVAXUSD', 'FILUSD'
        ]
        
        # Filter to only include pairs that actually exist
        try:
            if not self._asset_pairs:
                await self.get_asset_pairs()
            
            return [pair for pair in popular if pair in self._asset_pairs]
            
        except Exception as e:
            logger.error(f"Error getting popular pairs: {e}")
            return popular  # Return the list anyway
    
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