# TradeByte Usage Examples

## Table of Contents
1. [Market Maker Strategy](#market-maker-strategy)
2. [Data Collection](#data-collection)
3. [API Usage](#api-usage)
4. [Configuration Examples](#configuration-examples)
5. [WebSocket Usage](#websocket-usage)
6. [Rust Integration](#rust-integration)

## Market Maker Strategy

### Basic Market Maker Setup

```python
import asyncio
from src.apps.strategies.market_maker import MarketMaker

async def run_market_maker():
    strategy = MarketMaker()
    try:
        await strategy.start()
    except KeyboardInterrupt:
        await strategy.stop()

if __name__ == "__main__":
    asyncio.run(run_market_maker())
```

### Custom Market Maker Configuration

```python
class CustomMarketMaker(MarketMaker):
    def __init__(self):
        super().__init__()
        # Custom parameters
        self.pair = 'BTC/USD'
        self.bid_spread = Decimal('5')    # 5 basis points
        self.ask_spread = Decimal('5')    # 5 basis points
        self.min_order = Decimal('50')    # Minimum order size
        self.max_order = Decimal('500')   # Maximum order size
        self.ladder_size = 3              # 3 orders per side
```

### Running with Auto-Restart

The market maker automatically restarts on connection loss:

```python
async def main():
    while True:
        strategy = MarketMaker()
        try:
            await strategy.start()
        except KeyboardInterrupt:
            await strategy.stop()
            break
        except Exception as e:
            logger.error(f"Strategy error: {e}")
            await strategy.stop()
        
        logger.info("Restarting in 5 seconds...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
```

## Data Collection

### Collecting Market Data

```python
from src.apps.data_collector.kraken_data import KrakenDataCollector

async def collect_market_data():
    collector = KrakenDataCollector()
    
    # Collect order book data
    await collector.subscribe_orderbook(['BTC/USD', 'ETH/USD'])
    
    # Collect trade data
    await collector.subscribe_trades(['BTC/USD'])
    
    # Run for specified duration
    await asyncio.sleep(3600)  # 1 hour
    await collector.stop()

if __name__ == "__main__":
    asyncio.run(collect_market_data())
```

### Historical Data Analysis

```python
import json
import pandas as pd

def analyze_historical_data():
    # Load price data
    with open('data/btc_prices.json', 'r') as f:
        price_data = json.load(f)
    
    # Convert to DataFrame
    df = pd.DataFrame(price_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Calculate moving averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    return df
```

## API Usage

### Kraken REST API

```python
from src.clients.kraken_python_client import KrakenClient

async def kraken_api_example():
    client = KrakenClient()
    
    # Get account balance
    balance = await client.get_balance()
    print(f"Account balance: {balance}")
    
    # Get order book
    orderbook = await client.get_orderbook('BTC/USD', depth=10)
    print(f"Order book: {orderbook}")
    
    # Place a limit order
    order = await client.add_order(
        pair='BTC/USD',
        type='buy',
        ordertype='limit',
        volume='0.001',
        price='50000'
    )
    print(f"Order placed: {order}")
```

### WebSocket API

```python
from kraken_ws import KrakenWebSocket

async def websocket_example():
    client = KrakenWebSocket()
    
    # Connect to public WebSocket
    await client.connect()
    
    # Subscribe to order book
    await client.subscribe_book(['BTC/USD'], depth=10)
    
    # Define message handler
    async def handle_message(data):
        print(f"Received: {data}")
    
    # Add handler
    client.add_handler('book', handle_message)
    
    # Run the client
    await client.run()
```

## Configuration Examples

### Basic Configuration (`config/config.yaml`)

```yaml
kraken:
  api_key: "your_api_key_here"
  api_secret: "your_api_secret_here"
  sandbox: false  # Set to true for testing

trading:
  default_pair: "BTC/USD"
  max_position_size: 1000
  min_order_size: 10
  max_order_size: 1000

risk_management:
  max_daily_loss: 100
  max_position_risk: 0.02  # 2% per position
  stop_loss_pct: 0.05      # 5% stop loss

logging:
  level: "INFO"
  file: "logs/tradebyte.log"
  max_size: "10MB"
  backup_count: 5

websocket:
  ping_interval: 20
  ping_timeout: 10
  reconnect_delay: 5
```

### Strategy-Specific Configuration

```yaml
strategies:
  market_maker:
    enabled: true
    pairs:
      - "BTC/USD"
      - "ETH/USD"
    parameters:
      bid_spread: 5      # basis points
      ask_spread: 5      # basis points
      ladder_size: 5     # orders per side
      min_order: 10
      max_order: 1000
      update_interval: 1  # seconds
    
  data_collector:
    enabled: true
    pairs:
      - "BTC/USD"
      - "ETH/USD"
      - "ADA/USD"
    data_types:
      - "ticker"
      - "orderbook"
      - "trades"
    storage:
      format: "json"
      directory: "data/historical"
```

## WebSocket Usage

### Custom Message Handler

```python
from kraken_ws import KrakenWebSocket
import json

class CustomWebSocketClient(KrakenWebSocket):
    async def handle_orderbook_update(self, data):
        """Custom order book handler"""
        if isinstance(data, list) and len(data) >= 3:
            pair = data[2]
            orderbook = data[1]
            
            # Process order book data
            best_bid = max(orderbook.get('b', []), key=lambda x: float(x[0]))
            best_ask = min(orderbook.get('a', []), key=lambda x: float(x[0]))
            
            print(f"{pair}: Bid={best_bid[0]}, Ask={best_ask[0]}")
    
    async def handle_trade_update(self, data):
        """Custom trade handler"""
        if isinstance(data, list) and len(data) >= 3:
            trades = data[1]
            for trade in trades:
                price, volume, time, side = trade
                print(f"Trade: {side} {volume} @ {price}")

async def run_custom_client():
    client = CustomWebSocketClient()
    await client.connect()
    
    # Add custom handlers
    client.add_handler('book', client.handle_orderbook_update)
    client.add_handler('trade', client.handle_trade_update)
    
    # Subscribe to data
    await client.subscribe_book(['BTC/USD'], depth=10)
    await client.subscribe_trades(['BTC/USD'])
    
    await client.run()
```

### Error Handling and Recovery

```python
from kraken_ws import KrakenWebSocket
import asyncio
import logging

logger = logging.getLogger(__name__)

class RobustWebSocketClient(KrakenWebSocket):
    def __init__(self, max_retries=5):
        super().__init__()
        self.max_retries = max_retries
        self.retry_count = 0
    
    async def run_with_recovery(self):
        """Run with automatic recovery"""
        while self.retry_count < self.max_retries:
            try:
                await self.run()
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.retry_count += 1
                
                if self.retry_count < self.max_retries:
                    logger.info(f"Retrying in 5 seconds... (attempt {self.retry_count})")
                    await asyncio.sleep(5)
                    await self.connect()
                else:
                    logger.error("Max retries reached. Stopping.")
                    break
```

## Rust Integration

### Using Rust Functions in Python

```python
from rust_client import get_bid, get_ask, get_orderbook

def rust_api_example():
    # Get real-time prices
    bid_price = get_bid("BTC/USD")
    ask_price = get_ask("BTC/USD")
    
    print(f"BTC/USD - Bid: {bid_price}, Ask: {ask_price}")
    
    # Get order book
    orderbook = get_orderbook("BTC/USD", depth=10)
    print(f"Order book: {orderbook}")

if __name__ == "__main__":
    rust_api_example()
```

### Performance Comparison

```python
import time
from rust_client import get_bid as rust_get_bid
from src.clients.kraken_python_client import KrakenClient

async def performance_comparison():
    client = KrakenClient()
    
    # Python implementation
    start_time = time.time()
    for _ in range(100):
        await client.get_bid("BTC/USD")
    python_time = time.time() - start_time
    
    # Rust implementation
    start_time = time.time()
    for _ in range(100):
        rust_get_bid("BTC/USD")
    rust_time = time.time() - start_time
    
    print(f"Python: {python_time:.3f}s")
    print(f"Rust: {rust_time:.3f}s")
    print(f"Speedup: {python_time/rust_time:.1f}x")
```

## Advanced Examples

### Multi-Strategy Portfolio

```python
import asyncio
from src.apps.strategies.market_maker import MarketMaker
from src.apps.portfolio_manager.portfolio_trader import PortfolioManager

class MultiStrategyPortfolio:
    def __init__(self):
        self.strategies = {}
        self.portfolio_manager = PortfolioManager()
    
    async def add_strategy(self, name, strategy):
        self.strategies[name] = strategy
    
    async def run_all_strategies(self):
        tasks = []
        for name, strategy in self.strategies.items():
            task = asyncio.create_task(strategy.start())
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_all_strategies(self):
        for strategy in self.strategies.values():
            await strategy.stop()

async def run_multi_strategy():
    portfolio = MultiStrategyPortfolio()
    
    # Add market maker for BTC
    btc_mm = MarketMaker()
    btc_mm.pair = 'BTC/USD'
    await portfolio.add_strategy('BTC_MarketMaker', btc_mm)
    
    # Add market maker for ETH
    eth_mm = MarketMaker()
    eth_mm.pair = 'ETH/USD'
    await portfolio.add_strategy('ETH_MarketMaker', eth_mm)
    
    try:
        await portfolio.run_all_strategies()
    except KeyboardInterrupt:
        await portfolio.stop_all_strategies()
```

### Real-time Monitoring

```python
import asyncio
import json
from datetime import datetime
from kraken_ws import KrakenWebSocket

class TradingMonitor:
    def __init__(self):
        self.client = KrakenWebSocket()
        self.metrics = {
            'total_orders': 0,
            'total_volume': 0,
            'pnl': 0,
            'last_update': None
        }
    
    async def monitor_trades(self):
        await self.client.connect()
        await self.client.subscribe_trades(['BTC/USD'])
        
        async def handle_trade(data):
            if isinstance(data, list) and len(data) >= 3:
                trades = data[1]
                for trade in trades:
                    price, volume, time, side = trade
                    self.metrics['total_volume'] += float(volume)
                    self.metrics['last_update'] = datetime.now()
                    
                    print(f"Trade: {side} {volume} BTC @ ${price}")
                    print(f"Total volume: {self.metrics['total_volume']:.4f} BTC")
        
        self.client.add_handler('trade', handle_trade)
        await self.client.run()

async def run_monitor():
    monitor = TradingMonitor()
    await monitor.monitor_trades()

if __name__ == "__main__":
    asyncio.run(run_monitor())
```

These examples demonstrate the key features and capabilities of the TradeByte platform. Each example can be customized and extended based on your specific trading requirements.
