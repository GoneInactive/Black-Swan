import asyncio
import logging
from typing import Dict, Optional
from decimal import Decimal
import time
from api.kraken_ws import KrakenWebSocketClient

logger = logging.getLogger(__name__)

class EURQMarketMaker:
    """
    Market Maker implementation for EUR/USD trading on Kraken.
    Uses WebSocket for real-time market data and order management.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.client = KrakenWebSocketClient(config_path)
        self.pair = "EUR/USD"
        self.spread_multiplier = Decimal('1.0002')  # 2 basis points
        self.position_limit = Decimal('100000')     # Maximum position size
        self.current_position = Decimal('0')
        self.best_bid = None
        self.best_ask = None
        self.active_orders = {}
        self.running = False
        
    def start(self):
        """Start the market maker."""
        self.running = True
        self.client.start()
        
        # Register callbacks
        self.client.register_callback("ticker", self._handle_ticker)
        self.client.register_callback("ownTrades", self._handle_trades, is_private=True)
        
        # Start the main loop
        asyncio.create_task(self._run())
        
    async def _run(self):
        """Main market maker loop."""
        try:
            # Subscribe to market data
            await self.client.subscribe_ticker(self.pair)
            await self.client.subscribe_own_trades()
            
            while self.running:
                if self.best_bid and self.best_ask:
                    await self._update_quotes()
                await asyncio.sleep(1)  # Check every second
                
        except Exception as e:
            logger.error(f"Error in market maker loop: {e}")
            self.stop()
            
    async def _update_quotes(self):
        """Update market maker quotes based on current market conditions."""
        try:
            # Calculate our quotes
            mid_price = (self.best_bid + self.best_ask) / 2
            our_bid = mid_price / self.spread_multiplier
            our_ask = mid_price * self.spread_multiplier
            
            # Cancel existing orders
            await self._cancel_all_orders()
            
            # Place new orders if within position limits
            if self.current_position < self.position_limit:
                await self._place_order("buy", our_bid, Decimal('1000'))
            if self.current_position > -self.position_limit:
                await self._place_order("sell", our_ask, Decimal('1000'))
                
        except Exception as e:
            logger.error(f"Error updating quotes: {e}")
            
    async def _place_order(self, side: str, price: Decimal, size: Decimal):
        """Place a new order."""
        try:
            order = {
                "event": "addOrder",
                "ordertype": "limit",
                "type": side,
                "volume": str(size),
                "price": str(price),
                "pair": self.pair
            }
            await self.client.subscribe_private(order)
            logger.info(f"Placed {side} order: {size} @ {price}")
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            
    async def _cancel_all_orders(self):
        """Cancel all active orders."""
        try:
            for order_id in self.active_orders:
                cancel_msg = {
                    "event": "cancelOrder",
                    "txid": order_id
                }
                await self.client.subscribe_private(cancel_msg)
            self.active_orders.clear()
        except Exception as e:
            logger.error(f"Error canceling orders: {e}")
            
    def _handle_ticker(self, data: Dict):
        """Handle incoming ticker updates."""
        try:
            if isinstance(data, list) and len(data) > 1:
                ticker_data = data[1]
                self.best_bid = Decimal(str(ticker_data['b'][0]))
                self.best_ask = Decimal(str(ticker_data['a'][0]))
                logger.debug(f"Updated quotes - Bid: {self.best_bid}, Ask: {self.best_ask}")
        except Exception as e:
            logger.error(f"Error handling ticker: {e}")
            
    def _handle_trades(self, data: Dict):
        """Handle incoming trade updates."""
        try:
            if isinstance(data, list) and len(data) > 1:
                trades = data[1]
                for trade in trades:
                    side = trade.get('type', '').lower()
                    size = Decimal(str(trade.get('vol', '0')))
                    if side == 'buy':
                        self.current_position += size
                    else:
                        self.current_position -= size
                logger.info(f"Updated position: {self.current_position}")
        except Exception as e:
            logger.error(f"Error handling trades: {e}")
            
    def stop(self):
        """Stop the market maker."""
        self.running = False
        asyncio.create_task(self._cancel_all_orders())
        self.client.stop()
        
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start market maker
    mm = EURQMarketMaker()
    mm.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down market maker...")
        mm.stop() 