# TradeByte Development Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Code Standards](#code-standards)
4. [Testing](#testing)
5. [Contributing](#contributing)
6. [Architecture Patterns](#architecture-patterns)
7. [Debugging](#debugging)
8. [Performance Optimization](#performance-optimization)

## Getting Started

### Prerequisites

Before contributing to TradeByte, ensure you have the following installed:

```bash
# Required software
- Python 3.10+
- Rust 1.70+
- Git
- Docker (optional)
- VS Code or PyCharm (recommended)

# Python packages for development
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/GoneInactive/TradeByte.git
cd TradeByte

# Create development branch
git checkout -b feature/your-feature-name

# Set up pre-commit hooks
pip install pre-commit
pre-commit install

# Install development dependencies
pip install -r requirements-dev.txt
```

### Project Structure

```
TradeByte/
├── src/                    # Main source code
│   ├── apps/              # Application modules
│   │   ├── strategies/    # Trading strategies
│   │   ├── data-collector/# Data collection
│   │   └── execution/     # Order execution
│   ├── clients/           # API clients
│   ├── utils/             # Utility functions
│   └── handler/           # Command handling
├── kraken_ws/             # WebSocket implementation
├── rust_client/           # Rust components
├── tests/                 # Test suite
├── docs/                  # Documentation
├── config/                # Configuration files
└── scripts/               # Development scripts
```

## Development Environment

### IDE Configuration

#### VS Code Settings

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true
    }
}
```

#### PyCharm Configuration

1. **Project Interpreter**: Set to virtual environment
2. **Code Style**: Configure Black formatter
3. **Testing**: Configure pytest
4. **Linting**: Enable pylint and flake8

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pycqa/pylint
    rev: v2.17.4
    hooks:
      - id: pylint
        args: [--rcfile=.pylintrc]
```

### Development Scripts

```bash
# scripts/dev-setup.sh
#!/bin/bash

echo "Setting up TradeByte development environment..."

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Build Rust components
cd rust_client
maturin develop
cd ..

# Run initial tests
pytest tests/ -v

echo "Development environment setup complete!"
```

## Code Standards

### Python Style Guide

#### General Principles

1. **PEP 8 Compliance**: Follow PEP 8 style guidelines
2. **Type Hints**: Use type hints for all function parameters and return values
3. **Docstrings**: Include comprehensive docstrings for all functions and classes
4. **Error Handling**: Use specific exception types and provide meaningful error messages

#### Code Example

```python
from typing import Dict, List, Optional, Union
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class OrderManager:
    """
    Manages order placement and tracking for trading strategies.
    
    This class handles the lifecycle of trading orders, including
    placement, modification, and cancellation.
    """
    
    def __init__(self, client: 'KrakenClient') -> None:
        """
        Initialize the OrderManager.
        
        Args:
            client: Kraken API client instance
        """
        self.client = client
        self.active_orders: Dict[str, Dict] = {}
        self.order_history: List[Dict] = []
    
    async def place_order(
        self,
        pair: str,
        side: str,
        volume: Union[str, Decimal],
        price: Optional[Union[str, Decimal]] = None,
        order_type: str = 'limit'
    ) -> Dict[str, str]:
        """
        Place a new order on the exchange.
        
        Args:
            pair: Trading pair (e.g., 'BTC/USD')
            side: Order side ('buy' or 'sell')
            volume: Order volume
            price: Order price (required for limit orders)
            order_type: Type of order ('market', 'limit', etc.)
        
        Returns:
            Dictionary containing order response with 'status' and 'txid'
        
        Raises:
            ValueError: If required parameters are missing
            OrderError: If order placement fails
        """
        if not pair or not side or not volume:
            raise ValueError("pair, side, and volume are required")
        
        if order_type == 'limit' and not price:
            raise ValueError("price is required for limit orders")
        
        try:
            response = await self.client.add_order(
                pair=pair,
                type=side,
                ordertype=order_type,
                volume=str(volume),
                price=str(price) if price else None
            )
            
            if response.get('status') == 'ok':
                txid = response.get('txid')
                self.active_orders[txid] = {
                    'pair': pair,
                    'side': side,
                    'volume': volume,
                    'price': price,
                    'type': order_type
                }
                logger.info(f"Order placed successfully: {txid}")
                return response
            else:
                raise OrderError(f"Order placement failed: {response}")
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise OrderError(f"Order placement failed: {e}")
    
    def get_active_orders(self) -> Dict[str, Dict]:
        """
        Get all active orders.
        
        Returns:
            Dictionary of active orders indexed by transaction ID
        """
        return self.active_orders.copy()
    
    def get_order_history(self) -> List[Dict]:
        """
        Get order history.
        
        Returns:
            List of completed orders
        """
        return self.order_history.copy()
```

### Rust Style Guide

#### General Principles

1. **Rust Book Guidelines**: Follow the Rust Book style guidelines
2. **Error Handling**: Use Result and Option types appropriately
3. **Documentation**: Include comprehensive documentation comments
4. **Testing**: Write unit tests for all public functions

#### Code Example

```rust
//! Kraken API client implementation
//! 
//! This module provides high-performance functions for interacting
//! with the Kraken exchange API.

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use anyhow::{Result, Context};

/// Configuration for the Kraken API client
#[derive(Debug, Clone)]
pub struct KrakenConfig {
    pub api_key: String,
    pub api_secret: String,
    pub base_url: String,
    pub timeout: std::time::Duration,
}

impl Default for KrakenConfig {
    fn default() -> Self {
        Self {
            api_key: String::new(),
            api_secret: String::new(),
            base_url: "https://api.kraken.com".to_string(),
            timeout: std::time::Duration::from_secs(30),
        }
    }
}

/// Kraken API client
pub struct KrakenClient {
    config: KrakenConfig,
    client: Client,
}

impl KrakenClient {
    /// Create a new Kraken API client
    /// 
    /// # Arguments
    /// 
    /// * `config` - Configuration for the client
    /// 
    /// # Returns
    /// 
    /// A new KrakenClient instance
    /// 
    /// # Example
    /// 
    /// ```rust
    /// use tradebyte::kraken::KrakenClient;
    /// 
    /// let config = KrakenConfig::default();
    /// let client = KrakenClient::new(config);
    /// ```
    pub fn new(config: KrakenConfig) -> Result<Self> {
        let client = Client::builder()
            .timeout(config.timeout)
            .build()
            .context("Failed to create HTTP client")?;
        
        Ok(Self { config, client })
    }
    
    /// Get the current bid price for a trading pair
    /// 
    /// # Arguments
    /// 
    /// * `pair` - Trading pair (e.g., "BTCUSD")
    /// 
    /// # Returns
    /// 
    /// The current bid price as a f64
    /// 
    /// # Errors
    /// 
    /// Returns an error if the API request fails
    pub async fn get_bid(&self, pair: &str) -> Result<f64> {
        let url = format!("{}/0/public/Ticker", self.config.base_url);
        let params = [("pair", pair)];
        
        let response = self.client
            .get(&url)
            .query(&params)
            .send()
            .await
            .context("Failed to send API request")?;
        
        let data: HashMap<String, serde_json::Value> = response
            .json()
            .await
            .context("Failed to parse API response")?;
        
        // Extract bid price from response
        let ticker = data.get("result")
            .and_then(|r| r.get(pair))
            .context("Invalid API response format")?;
        
        let bid = ticker.get("b")
            .and_then(|b| b.get(0))
            .and_then(|v| v.as_str())
            .context("Bid price not found in response")?;
        
        bid.parse::<f64>()
            .context("Failed to parse bid price")
    }
    
    /// Get the current ask price for a trading pair
    /// 
    /// # Arguments
    /// 
    /// * `pair` - Trading pair (e.g., "BTCUSD")
    /// 
    /// # Returns
    /// 
    /// The current ask price as a f64
    /// 
    /// # Errors
    /// 
    /// Returns an error if the API request fails
    pub async fn get_ask(&self, pair: &str) -> Result<f64> {
        let url = format!("{}/0/public/Ticker", self.config.base_url);
        let params = [("pair", pair)];
        
        let response = self.client
            .get(&url)
            .query(&params)
            .send()
            .await
            .context("Failed to send API request")?;
        
        let data: HashMap<String, serde_json::Value> = response
            .json()
            .await
            .context("Failed to parse API response")?;
        
        // Extract ask price from response
        let ticker = data.get("result")
            .and_then(|r| r.get(pair))
            .context("Invalid API response format")?;
        
        let ask = ticker.get("a")
            .and_then(|a| a.get(0))
            .and_then(|v| v.as_str())
            .context("Ask price not found in response")?;
        
        ask.parse::<f64>()
            .context("Failed to parse ask price")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_get_bid() {
        let config = KrakenConfig::default();
        let client = KrakenClient::new(config).unwrap();
        
        let bid = client.get_bid("XBTUSD").await;
        assert!(bid.is_ok());
        assert!(bid.unwrap() > 0.0);
    }
    
    #[tokio::test]
    async fn test_get_ask() {
        let config = KrakenConfig::default();
        let client = KrakenClient::new(config).unwrap();
        
        let ask = client.get_ask("XBTUSD").await;
        assert!(ask.is_ok());
        assert!(ask.unwrap() > 0.0);
    }
}
```

## Testing

### Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_strategies/   # Strategy tests
│   ├── test_clients/      # Client tests
│   └── test_utils/        # Utility tests
├── integration/           # Integration tests
├── fixtures/              # Test data
└── conftest.py           # Pytest configuration
```

### Unit Testing

```python
# tests/unit/test_order_manager.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from src.clients.order_manager import OrderManager, OrderError

class TestOrderManager:
    """Test cases for OrderManager class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Kraken client."""
        client = AsyncMock()
        client.add_order = AsyncMock()
        return client
    
    @pytest.fixture
    def order_manager(self, mock_client):
        """Create OrderManager instance with mock client."""
        return OrderManager(mock_client)
    
    @pytest.mark.asyncio
    async def test_place_order_success(self, order_manager, mock_client):
        """Test successful order placement."""
        # Arrange
        mock_client.add_order.return_value = {
            'status': 'ok',
            'txid': 'O123456-ABCDEF-GHIJKL'
        }
        
        # Act
        result = await order_manager.place_order(
            pair='BTC/USD',
            side='buy',
            volume=Decimal('0.001'),
            price=Decimal('50000')
        )
        
        # Assert
        assert result['status'] == 'ok'
        assert result['txid'] == 'O123456-ABCDEF-GHIJKL'
        assert len(order_manager.active_orders) == 1
        mock_client.add_order.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_place_order_failure(self, order_manager, mock_client):
        """Test order placement failure."""
        # Arrange
        mock_client.add_order.return_value = {
            'status': 'error',
            'error': ['Insufficient funds']
        }
        
        # Act & Assert
        with pytest.raises(OrderError, match="Order placement failed"):
            await order_manager.place_order(
                pair='BTC/USD',
                side='buy',
                volume=Decimal('0.001'),
                price=Decimal('50000')
            )
    
    def test_get_active_orders(self, order_manager):
        """Test getting active orders."""
        # Arrange
        order_manager.active_orders = {
            'txid1': {'pair': 'BTC/USD', 'side': 'buy'},
            'txid2': {'pair': 'ETH/USD', 'side': 'sell'}
        }
        
        # Act
        result = order_manager.get_active_orders()
        
        # Assert
        assert len(result) == 2
        assert 'txid1' in result
        assert 'txid2' in result
        assert result['txid1']['pair'] == 'BTC/USD'
    
    @pytest.mark.parametrize("pair,side,volume,price,expected_error", [
        ("", "buy", "0.001", "50000", "pair, side, and volume are required"),
        ("BTC/USD", "", "0.001", "50000", "pair, side, and volume are required"),
        ("BTC/USD", "buy", "", "50000", "pair, side, and volume are required"),
        ("BTC/USD", "buy", "0.001", None, "price is required for limit orders"),
    ])
    @pytest.mark.asyncio
    async def test_place_order_validation(self, order_manager, pair, side, volume, price, expected_error):
        """Test order parameter validation."""
        with pytest.raises(ValueError, match=expected_error):
            await order_manager.place_order(
                pair=pair,
                side=side,
                volume=volume,
                price=price
            )
```

### Integration Testing

```python
# tests/integration/test_market_maker.py
import pytest
import asyncio
from decimal import Decimal
from src.apps.strategies.market_maker import MarketMaker

class TestMarketMakerIntegration:
    """Integration tests for MarketMaker strategy."""
    
    @pytest.fixture
    def market_maker(self):
        """Create MarketMaker instance for testing."""
        strategy = MarketMaker()
        strategy.pair = 'BTC/USD'
        strategy.bid_spread = Decimal('10')
        strategy.ask_spread = Decimal('10')
        strategy.min_order = Decimal('10')
        strategy.max_order = Decimal('100')
        return strategy
    
    @pytest.mark.asyncio
    async def test_market_maker_initialization(self, market_maker):
        """Test MarketMaker initialization."""
        assert market_maker.pair == 'BTC/USD'
        assert market_maker.bid_spread == Decimal('10')
        assert market_maker.ask_spread == Decimal('10')
        assert market_maker.build_first_book is True
    
    @pytest.mark.asyncio
    async def test_generate_ladder(self, market_maker):
        """Test ladder generation."""
        base_price = Decimal('50000')
        total_size = Decimal('100')
        
        # Test buy ladder
        buy_ladder = market_maker.generate_ladder(base_price, total_size, 'buy')
        assert len(buy_ladder) == 5  # Fixed ladder size
        assert buy_ladder[0][1] == base_price  # First order at base price
        assert buy_ladder[1][1] == base_price + market_maker.ladder_increment
        
        # Test sell ladder
        sell_ladder = market_maker.generate_ladder(base_price, total_size, 'sell')
        assert len(sell_ladder) == 5
        assert sell_ladder[0][1] == base_price
        assert sell_ladder[1][1] == base_price - market_maker.ladder_increment
    
    @pytest.mark.asyncio
    async def test_generate_positions(self, market_maker):
        """Test position size generation."""
        asset_price = Decimal('50000')
        asset_balance = Decimal('1.0')
        currency_balance = Decimal('50000')
        
        buy_size, sell_size = market_maker.generate_positions(
            asset_price, asset_balance, currency_balance
        )
        
        # Should be balanced (50/50 split)
        assert buy_size > 0
        assert sell_size > 0
        assert buy_size <= market_maker.max_order
        assert sell_size <= market_maker.max_order
```

### Performance Testing

```python
# tests/performance/test_websocket_performance.py
import pytest
import asyncio
import time
from kraken_ws import KrakenWebSocket

class TestWebSocketPerformance:
    """Performance tests for WebSocket client."""
    
    @pytest.mark.asyncio
    async def test_message_processing_speed(self):
        """Test WebSocket message processing speed."""
        client = KrakenWebSocket()
        message_count = 1000
        processing_times = []
        
        async def message_handler(data):
            start_time = time.time()
            # Simulate message processing
            await asyncio.sleep(0.001)
            processing_times.append(time.time() - start_time)
        
        client.add_handler('book', message_handler)
        
        # Simulate messages
        start_time = time.time()
        for _ in range(message_count):
            await client._handle_public_message('{"test": "data"}')
        
        total_time = time.time() - start_time
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        # Assertions
        assert total_time < 5.0  # Should process 1000 messages in under 5 seconds
        assert avg_processing_time < 0.01  # Average processing time under 10ms
    
    @pytest.mark.asyncio
    async def test_connection_recovery_speed(self):
        """Test WebSocket connection recovery speed."""
        client = KrakenWebSocket()
        
        # Simulate connection loss and recovery
        start_time = time.time()
        
        # Mock connection loss
        client._ws_connection = None
        client.is_connected = False
        
        # Attempt reconnection
        await client.connect()
        
        recovery_time = time.time() - start_time
        
        # Should recover quickly
        assert recovery_time < 10.0  # Recovery under 10 seconds
```

### Test Configuration

```python
# tests/conftest.py
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_kraken_client():
    """Create a mock Kraken client for testing."""
    client = AsyncMock()
    client.add_order = AsyncMock()
    client.get_balance = AsyncMock()
    client.get_orderbook = AsyncMock()
    return client

@pytest.fixture
def sample_orderbook_data():
    """Sample order book data for testing."""
    return {
        'bids': [
            ['50000.0', '1.5', '1234567890'],
            ['49999.0', '2.0', '1234567891'],
            ['49998.0', '0.5', '1234567892']
        ],
        'asks': [
            ['50001.0', '1.0', '1234567893'],
            ['50002.0', '2.5', '1234567894'],
            ['50003.0', '0.8', '1234567895']
        ]
    }

@pytest.fixture
def sample_trade_data():
    """Sample trade data for testing."""
    return [
        ['50000.5', '0.1', '1234567890', 'b', 'l', ''],
        ['50000.3', '0.2', '1234567891', 's', 'm', ''],
        ['50000.7', '0.05', '1234567892', 'b', 'l', '']
    ]
```

## Contributing

### Development Workflow

1. **Fork the Repository**: Create your own fork of the TradeByte repository
2. **Create Feature Branch**: Create a new branch for your feature
3. **Make Changes**: Implement your changes following the code standards
4. **Write Tests**: Add comprehensive tests for your changes
5. **Run Tests**: Ensure all tests pass
6. **Submit Pull Request**: Create a pull request with detailed description

### Pull Request Guidelines

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Performance tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] No new warnings generated
- [ ] Added tests that prove the fix is effective or that the feature works

## Additional Notes
Any additional information that reviewers should know.
```

### Code Review Process

1. **Automated Checks**: All PRs must pass automated checks
2. **Code Review**: At least one maintainer must approve
3. **Testing**: All tests must pass
4. **Documentation**: Documentation must be updated if needed

## Architecture Patterns

### Strategy Pattern

```python
# src/strategies/base_strategy.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio

class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.performance_metrics = {}
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the strategy."""
        pass
    
    @abstractmethod
    async def on_market_update(self, data: Dict[str, Any]) -> None:
        """Handle market data updates."""
        pass
    
    @abstractmethod
    async def execute_trades(self, signals: list) -> None:
        """Execute trades based on signals."""
        pass
    
    async def start(self) -> None:
        """Start the strategy."""
        self.running = True
        await self.initialize()
        logger.info(f"Strategy {self.__class__.__name__} started")
    
    async def stop(self) -> None:
        """Stop the strategy."""
        self.running = False
        logger.info(f"Strategy {self.__class__.__name__} stopped")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics."""
        return self.performance_metrics.copy()
```

### Observer Pattern

```python
# src/utils/event_system.py
from typing import Callable, Dict, List
import asyncio

class EventSystem:
    """Event system for decoupled communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event to all subscribers."""
        if event_type in self._subscribers:
            tasks = []
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(asyncio.create_task(callback(data)))
                else:
                    callback(data)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

# Global event system
event_system = EventSystem()
```

### Factory Pattern

```python
# src/strategies/strategy_factory.py
from typing import Dict, Type
from .base_strategy import BaseStrategy
from .market_maker import MarketMaker

class StrategyFactory:
    """Factory for creating strategy instances."""
    
    _strategies: Dict[str, Type[BaseStrategy]] = {
        'market_maker': MarketMaker,
        # Add more strategies here
    }
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[BaseStrategy]) -> None:
        """Register a new strategy class."""
        cls._strategies[name] = strategy_class
    
    @classmethod
    def create_strategy(cls, name: str, config: Dict[str, Any]) -> BaseStrategy:
        """Create a strategy instance."""
        if name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        
        strategy_class = cls._strategies[name]
        return strategy_class(config)
    
    @classmethod
    def list_strategies(cls) -> List[str]:
        """List all available strategies."""
        return list(cls._strategies.keys())

# Usage
strategy = StrategyFactory.create_strategy('market_maker', config)
```

## Debugging

### Debug Configuration

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Market Maker",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/apps/strategies/market_maker.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "LOG_LEVEL": "DEBUG"
            },
            "args": []
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v", "-s"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Debugging Tools

```python
# src/utils/debug.py
import logging
import time
import functools
from typing import Any, Callable

def debug_function(func: Callable) -> Callable:
    """Decorator to debug function calls."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        logger.debug(f"Entering {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Exiting {func.__name__} in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in {func.__name__} after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

class PerformanceProfiler:
    """Performance profiler for debugging."""
    
    def __init__(self):
        self.measurements = {}
    
    def start(self, name: str) -> None:
        """Start timing an operation."""
        self.measurements[name] = time.time()
    
    def end(self, name: str) -> float:
        """End timing an operation and return duration."""
        if name in self.measurements:
            duration = time.time() - self.measurements[name]
            del self.measurements[name]
            return duration
        return 0.0
    
    def get_measurements(self) -> Dict[str, float]:
        """Get all measurements."""
        return self.measurements.copy()

# Global profiler
profiler = PerformanceProfiler()
```

## Performance Optimization

### Profiling

```python
# scripts/profile.py
import cProfile
import pstats
import io
from src.apps.strategies.market_maker import MarketMaker

def profile_market_maker():
    """Profile the market maker strategy."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run the strategy for a short time
    strategy = MarketMaker()
    # ... run strategy ...
    
    profiler.disable()
    
    # Print results
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(20)
    print(s.getvalue())

if __name__ == "__main__":
    profile_market_maker()
```

### Memory Profiling

```python
# scripts/memory_profile.py
import tracemalloc
from src.apps.strategies.market_maker import MarketMaker

def memory_profile():
    """Profile memory usage."""
    tracemalloc.start()
    
    # Run the strategy
    strategy = MarketMaker()
    # ... run strategy ...
    
    # Get memory snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("[ Top 10 memory users ]")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()

if __name__ == "__main__":
    memory_profile()
```

This comprehensive development guide provides all the information needed to contribute to the TradeByte platform effectively. It covers coding standards, testing practices, architecture patterns, and debugging techniques to ensure high-quality contributions. 