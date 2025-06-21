# TradeByte API Reference

## Table of Contents
1. [Overview](#overview)
2. [WebSocket API](#websocket-api)
3. [REST API](#rest-api)
4. [Rust API](#rust-api)
5. [Strategy API](#strategy-api)
6. [Data API](#data-api)
7. [Configuration API](#configuration-api)
8. [Error Handling](#error-handling)

## Overview

TradeByte provides multiple API interfaces for different use cases:

- **WebSocket API**: Real-time market data and trading operations
- **REST API**: Traditional HTTP-based API for configuration and management
- **Rust API**: High-performance functions for critical operations
- **Strategy API**: Interface for custom trading strategies
- **Data API**: Market data access and management

## WebSocket API

### Connection

#### KrakenWebSocket Class

```python
from kraken_ws import KrakenWebSocket

# Initialize WebSocket client
client = KrakenWebSocket(api_key="your_key", api_secret="your_secret")

# Connect to WebSocket
await client.connect(private=True)  # private=True for authenticated connection
```

**Parameters:**
- `api_key` (str, optional): Kraken API key
- `api_secret` (str, optional): Kraken API secret

**Methods:**

#### connect(private=False)
Establishes WebSocket connection.

**Parameters:**
- `private` (bool): Whether to establish authenticated connection

**Returns:** None

**Example:**
```python
await client.connect(private=True)
```

#### subscribe_book(pairs, depth=10, handler=None)
Subscribe to order book data.

**Parameters:**
- `pairs` (List[str]): List of trading pairs
- `depth` (int): Order book depth (default: 10)
- `handler` (Callable, optional): Message handler function

**Returns:** None

**Example:**
```python
async def handle_orderbook(data):
    print(f"Order book update: {data}")

await client.subscribe_book(['BTC/USD'], depth=10, handler=handle_orderbook)
```

#### subscribe_trades(pairs, handler=None)
Subscribe to trade data.

**Parameters:**
- `pairs` (List[str]): List of trading pairs
- `handler` (Callable, optional): Message handler function

**Returns:** None

**Example:**
```python
async def handle_trades(data):
    print(f"Trade update: {data}")

await client.subscribe_trades(['BTC/USD'], handler=handle_trades)
```

#### add_handler(event_type, handler)
Add a message handler for specific event types.

**Parameters:**
- `event_type` (str): Event type (e.g., 'book', 'trade')
- `handler` (Callable): Handler function

**Returns:** None

**Example:**
```python
client.add_handler('book', handle_orderbook)
client.add_handler('trade', handle_trades)
```

#### run()
Start the WebSocket client and begin processing messages.

**Returns:** None

**Example:**
```python
await client.run()
```

#### close()
Close the WebSocket connection.

**Returns:** None

**Example:**
```python
await client.close()
```

### Account Operations

#### KrakenAccount Class

```python
from kraken_ws.account import KrakenAccount

# Initialize account client
account = KrakenAccount(api_key="your_key", api_secret="your_secret")

# Connect to authenticated WebSocket
await account.connect()
```

#### add_order(pair, type, ordertype, volume, price=None, validate=False, **kwargs)
Place a new order.

**Parameters:**
- `pair` (str): Trading pair
- `type` (str): Order type ('buy' or 'sell')
- `ordertype` (str): Order type ('market', 'limit', 'stop-loss', etc.)
- `volume` (str): Order volume
- `price` (str, optional): Order price
- `validate` (bool): Whether to validate only (default: False)
- `**kwargs`: Additional order parameters

**Returns:** Dict containing order response

**Example:**
```python
response = await account.add_order(
    pair='BTC/USD',
    type='buy',
    ordertype='limit',
    volume='0.001',
    price='50000'
)
```

#### edit_order(txid, volume=None, limit_price=None, **kwargs)
Edit an existing order.

**Parameters:**
- `txid` (str): Order transaction ID
- `volume` (str, optional): New volume
- `limit_price` (str, optional): New price
- `**kwargs`: Additional parameters

**Returns:** Dict containing edit response

**Example:**
```python
response = await account.edit_order(
    txid='O123456-ABCDEF-GHIJKL',
    volume='0.002',
    limit_price='51000'
)
```

#### cancel_order(txid)
Cancel one or more orders.

**Parameters:**
- `txid` (Union[str, List[str]]): Order transaction ID(s)

**Returns:** Dict containing cancel response

**Example:**
```python
# Cancel single order
response = await account.cancel_order('O123456-ABCDEF-GHIJKL')

# Cancel multiple orders
response = await account.cancel_order([
    'O123456-ABCDEF-GHIJKL',
    'O789012-MNOPQR-STUVWX'
])
```

#### cancel_all_orders()
Cancel all open orders.

**Returns:** Dict containing cancel response

**Example:**
```python
response = await account.cancel_all_orders()
```

## REST API

### Kraken REST Client

```python
from src.clients.kraken_python_client import KrakenClient

# Initialize REST client
client = KrakenClient(api_key="your_key", api_secret="your_secret")
```

#### get_balance()
Get account balance.

**Returns:** Dict containing account balances

**Example:**
```python
balance = await client.get_balance()
print(f"BTC Balance: {balance.get('XXBT', 0)}")
print(f"USD Balance: {balance.get('ZUSD', 0)}")
```

#### get_orderbook(pair, depth=10)
Get order book for a trading pair.

**Parameters:**
- `pair` (str): Trading pair
- `depth` (int): Order book depth (default: 10)

**Returns:** Dict containing order book data

**Example:**
```python
orderbook = await client.get_orderbook('BTC/USD', depth=20)
bids = orderbook['bids']
asks = orderbook['asks']
```

#### get_ticker(pair)
Get ticker information for a trading pair.

**Parameters:**
- `pair` (str): Trading pair

**Returns:** Dict containing ticker data

**Example:**
```python
ticker = await client.get_ticker('BTC/USD')
print(f"Last Price: {ticker['c'][0]}")
print(f"24h Volume: {ticker['v'][1]}")
```

#### get_recent_trades(pair, since=None)
Get recent trades for a trading pair.

**Parameters:**
- `pair` (str): Trading pair
- `since` (int, optional): Return committed trades since given ID

**Returns:** List containing recent trades

**Example:**
```python
trades = await client.get_recent_trades('BTC/USD')
for trade in trades:
    print(f"Price: {trade[0]}, Volume: {trade[1]}, Time: {trade[2]}")
```

#### get_open_orders()
Get open orders.

**Returns:** Dict containing open orders

**Example:**
```python
orders = await client.get_open_orders()
for txid, order in orders.items():
    print(f"Order {txid}: {order['descr']['pair']} {order['vol']} @ {order['descr']['price']}")
```

## Rust API

### High-Performance Functions

```python
from rust_client import get_bid, get_ask, get_orderbook

# Get real-time bid/ask prices
bid_price = get_bid("BTC/USD")
ask_price = get_ask("BTC/USD")
spread = ask_price - bid_price

print(f"Bid: ${bid_price:.2f}")
print(f"Ask: ${ask_price:.2f}")
print(f"Spread: ${spread:.2f}")
```

#### get_bid(pair)
Get current bid price for a trading pair.

**Parameters:**
- `pair` (str): Trading pair

**Returns:** float - Current bid price

**Example:**
```python
btc_bid = get_bid("BTC/USD")
eth_bid = get_bid("ETH/USD")
```

#### get_ask(pair)
Get current ask price for a trading pair.

**Parameters:**
- `pair` (str): Trading pair

**Returns:** float - Current ask price

**Example:**
```python
btc_ask = get_ask("BTC/USD")
eth_ask = get_ask("ETH/USD")
```

#### get_orderbook(pair, depth=10)
Get order book data.

**Parameters:**
- `pair` (str): Trading pair
- `depth` (int): Order book depth (default: 10)

**Returns:** Dict containing order book data

**Example:**
```python
orderbook = get_orderbook("BTC/USD", depth=20)
bids = orderbook['bids']
asks = orderbook['asks']
```

## Strategy API

### Market Maker Strategy

```python
from src.apps.strategies.market_maker import MarketMaker

# Initialize market maker
strategy = MarketMaker()

# Customize parameters
strategy.pair = 'BTC/USD'
strategy.bid_spread = Decimal('5')    # 5 basis points
strategy.ask_spread = Decimal('5')    # 5 basis points
strategy.min_order = Decimal('10')    # Minimum order size
strategy.max_order = Decimal('1000')  # Maximum order size
strategy.ladder_size = 5              # Orders per side

# Start the strategy
await strategy.start()
```

#### MarketMaker Class Methods

##### generate_ladder(base_price, total_size, side)
Generate a ladder of orders.

**Parameters:**
- `base_price` (Decimal): Base price for the ladder
- `total_size` (Decimal): Total order size
- `side` (str): 'buy' or 'sell'

**Returns:** List of [quantity, price] pairs

**Example:**
```python
ladder = strategy.generate_ladder(
    base_price=Decimal('50000'),
    total_size=Decimal('100'),
    side='buy'
)
```

##### generate_positions(asset_price, asset_balance, currency_balance)
Generate position sizes based on current balances.

**Parameters:**
- `asset_price` (Decimal): Current asset price
- `asset_balance` (Decimal): Current asset balance
- `currency_balance` (Decimal): Current currency balance

**Returns:** Tuple of (buy_size, sell_size)

**Example:**
```python
buy_size, sell_size = strategy.generate_positions(
    asset_price=Decimal('50000'),
    asset_balance=Decimal('1.0'),
    currency_balance=Decimal('50000')
)
```

##### update_orders_with_edits(new_ladder, side)
Update orders using edit operations when possible.

**Parameters:**
- `new_ladder` (List): New ladder of orders
- `side` (str): 'buy' or 'sell'

**Returns:** None

**Example:**
```python
await strategy.update_orders_with_edits(bid_ladder, 'buy')
await strategy.update_orders_with_edits(ask_ladder, 'sell')
```

### Custom Strategy Development

```python
from abc import ABC, abstractmethod
import asyncio

class BaseStrategy(ABC):
    def __init__(self, pair, client):
        self.pair = pair
        self.client = client
        self.running = False
    
    @abstractmethod
    async def on_market_update(self, data):
        """Handle market data updates"""
        pass
    
    @abstractmethod
    async def execute_trades(self, signals):
        """Execute trades based on signals"""
        pass
    
    async def start(self):
        """Start the strategy"""
        self.running = True
        await self.client.subscribe_book([self.pair], handler=self.on_market_update)
        await self.client.run()
    
    async def stop(self):
        """Stop the strategy"""
        self.running = False
        await self.client.close()

class MyCustomStrategy(BaseStrategy):
    async def on_market_update(self, data):
        """Custom market update handler"""
        if not self.running:
            return
        
        # Your strategy logic here
        signals = self.analyze_market(data)
        await self.execute_trades(signals)
    
    def analyze_market(self, data):
        """Analyze market data and generate signals"""
        # Your analysis logic here
        return []
    
    async def execute_trades(self, signals):
        """Execute trades based on signals"""
        for signal in signals:
            if signal['action'] == 'buy':
                await self.client.account.add_order(
                    pair=self.pair,
                    type='buy',
                    ordertype='limit',
                    volume=signal['volume'],
                    price=signal['price']
                )
```

## Data API

### Market Data Collection

```python
from src.apps.data_collector.kraken_data import KrakenDataCollector

# Initialize data collector
collector = KrakenDataCollector()

# Subscribe to market data
await collector.subscribe_orderbook(['BTC/USD', 'ETH/USD'])
await collector.subscribe_trades(['BTC/USD'])

# Run data collection
await collector.run()
```

### Historical Data Access

```python
import json
import pandas as pd
from pathlib import Path

def load_historical_data(symbol, data_type='prices'):
    """Load historical data from JSON files"""
    data_file = Path(f"data/{symbol}_{data_type}.json")
    
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    return pd.DataFrame(data)

# Load price data
btc_prices = load_historical_data('btc', 'prices')
eth_prices = load_historical_data('eth', 'prices')

# Convert timestamp to datetime
btc_prices['timestamp'] = pd.to_datetime(btc_prices['timestamp'], unit='s')
eth_prices['timestamp'] = pd.to_datetime(eth_prices['timestamp'], unit='s')
```

### Data Analysis Functions

```python
def calculate_technical_indicators(df):
    """Calculate technical indicators for a price DataFrame"""
    # Moving averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    return df

# Apply technical indicators
btc_prices = calculate_technical_indicators(btc_prices)
```

## Configuration API

### Configuration Management

```python
import yaml
from pathlib import Path

def load_config(config_path="config/config.yaml"):
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def save_config(config, config_path="config/config.yaml"):
    """Save configuration to YAML file"""
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def update_config(updates, config_path="config/config.yaml"):
    """Update specific configuration values"""
    config = load_config(config_path)
    
    # Recursively update nested dictionaries
    def update_nested(d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = update_nested(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    config = update_nested(config, updates)
    save_config(config, config_path)
    return config

# Example usage
config = load_config()

# Update trading parameters
updates = {
    'trading': {
        'max_position_size': 2000,
        'min_order_size': 20
    }
}

config = update_config(updates)
```

### Environment Variable Support

```python
import os
from typing import Optional

def get_config_value(key: str, default=None) -> Optional[str]:
    """Get configuration value from environment variable or config file"""
    # Check environment variable first
    env_key = f"TRADEBYTE_{key.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Fall back to config file
    config = load_config()
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value

# Example usage
api_key = get_config_value('kraken.api_key')
api_secret = get_config_value('kraken.api_secret')
max_position = get_config_value('trading.max_position_size', '1000')
```

## Error Handling

### Common Error Types

```python
class TradeByteError(Exception):
    """Base exception for TradeByte errors"""
    pass

class ConnectionError(TradeByteError):
    """WebSocket connection error"""
    pass

class AuthenticationError(TradeByteError):
    """API authentication error"""
    pass

class OrderError(TradeByteError):
    """Order placement/management error"""
    pass

class ConfigurationError(TradeByteError):
    """Configuration error"""
    pass
```

### Error Handling Examples

```python
import asyncio
from kraken_ws import KrakenWebSocket

async def robust_websocket_connection():
    """Example of robust WebSocket connection with error handling"""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            client = KrakenWebSocket()
            await client.connect(private=True)
            
            # Add error handlers
            async def handle_error(error):
                logger.error(f"WebSocket error: {error}")
            
            client.add_handler('error', handle_error)
            
            # Subscribe to data
            await client.subscribe_book(['BTC/USD'])
            
            # Run the client
            await client.run()
            
        except ConnectionError as e:
            retry_count += 1
            logger.warning(f"Connection failed (attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            else:
                logger.error("Max retries reached. Giving up.")
                raise
        
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

# Usage
try:
    asyncio.run(robust_websocket_connection())
except TradeByteError as e:
    print(f"TradeByte error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Logging Configuration

```python
import logging
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file="logs/tradebyte.log"):
    """Setup comprehensive logging for TradeByte"""
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger('tradebyte')

# Setup logging
logger = setup_logging()

# Usage in your code
logger.info("Application started")
logger.warning("High memory usage detected")
logger.error("Failed to place order")
```

This comprehensive API reference covers all the major interfaces and functions available in the TradeByte platform. Each section includes detailed parameter descriptions, return values, and practical examples to help you integrate and extend the platform for your specific needs. 