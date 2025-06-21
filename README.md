<img src="docs/images/tradebyte.PNG" alt="drawing" width="700"> 

# TradeByte - A Crypto-Exclusive Quantitative Trading Framework

TradeByte is a modular crypto trading bot platform built exclusively for Kraken, designed to help traders navigate volatile markets and seize rare opportunities. Whether you're backtesting strategies or executing live trades, TradeByte brings together strategy deployment, data analysis, and performance tracking in one flexible, streamlined system—built for serious crypto traders.

Together, Python and Rust combine to deliver a flexible yet powerful framework that supports both high-level strategy development and low-level system performance.

## Project Overview
TradeByte is a modular trading strategy manager designed for flexibility, performance, and extensibility. It allows users to create custom trading strategies, backtest them on historical data, paper trade in real-time without risking capital, and transition seamlessly into live trading. The platform also provides detailed analytics and performance statistics to help users evaluate and refine their strategies.

The project is built with Python and Rust, combining the ease and flexibility of Python for high-level strategy logic and orchestration, with the speed and safety of Rust for low-level performance-critical components. Python powers the strategy engine, configuration handling, and overall control flow, while Rust is used for communicating with the Kraken exchange, ensuring fast and reliable data fetching for bid/ask prices and other market data.

TradeByte is designed to be lightweight and adaptable—ideal for developers, quant enthusiasts, and traders who want full control over how their strategies are designed, tested, and executed.

## Features

- **Modular Strategy Engine** – Plug-and-play support for custom trading strategies (e.g., RSI, SMA, custom ML).
- **Kraken API Integration** – Built specifically to interface with Kraken's REST and WebSocket APIs.
- **Live & Paper Trading Modes** – Choose between real execution or simulation.
- **Backtesting Engine** – Test strategies against historical Kraken market data.
- **Logging & Performance Analytics** – Track trades, performance, and KPIs over time.
- **Secure Config Management** – Store keys and strategy parameters safely via config files.
- **Real-time Market Making** – Advanced market making strategy with automatic restart capabilities.
- **WebSocket Integration** – Robust WebSocket handling for real-time market data and order management.

## Recent Updates

### Market Maker Strategy Improvements
- **Automatic Restart**: The market maker strategy now automatically restarts if the connection is lost
- **Order Editing**: Implemented efficient order editing to minimize API calls and reduce latency
- **Fixed Ladder Size**: Standardized to 5 orders per side for consistent market making
- **Error Handling**: Enhanced error handling and logging for better debugging

### WebSocket Enhancements
- **Connection State Management**: Fixed WebSocket connection state checking for better reliability
- **Message Format Handling**: Improved handling of different Kraken WebSocket message formats
- **Robust Error Recovery**: Better error handling and recovery mechanisms

## Exchanges Supported

| Exchange              | Support Status       | Notes               |
|-----------------------|----------------------|---------------------|
| Kraken                | Fully supported      | REST & WebSocket APIs |
| Binance US            | Fully supported      | —                   |
| Binance International | Support coming soon  | Not yet available   |
| Hyperliquid           | Support coming soon  | Not yet available   |

---
## Getting Started & Installation 
### Prerequisites
- Python 3.10+
- Rust (with `maturin` installed)
- `pip`

### 1. Clone the repository
```bash
git clone https://github.com/GoneInactive/TradeByte.git
cd TradeByte
```

### 2. Set up your virtual environment

On Windows:
```bash
python -m venv venv
python -m source venv/Scripts/activate 
```
OR
```
python -m venv venv
venv\Scripts\activate.bat
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1     # Do this if error during maturin develop
```

On Mac:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Rust dependencies
```bash
cd rust_client
maturin develop
```

### 4. Install Python dependencies
```bash
cd ..  # If not already in main directory
pip install -r requirements.txt
```

### 5. Get your Kraken API keys
1. Sign into your Kraken account using Kraken Pro
2. Click on your profile (top right corner)
3. Select settings
4. Select the `API` tab
5. Click `Create API key`
6. Select appropriate permissions
7. Click `Generate key` at the bottom

### 6. Set up your configuration
Create a `config/config.yaml` file and paste your keys and adjust settings as necessary.

### 7. Run tests (Optional)
In the main directory, there are various tests to ensure the program is working properly.
```bash
python tests/(test).py
```

Example:
```bash
python tests/test_rust_client.py
```

### 8. Run the Market Maker Strategy
```bash
python src/apps/strategies/market_maker.py
```

---
## Project Structure
---
```
TradeByte/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── config/
│   └── config.yaml
├── kraken_ws/
│   ├── __init__.py
│   ├── kraken_ws.py          # Main WebSocket client
│   ├── account.py            # Account management
│   └── markets.py            # Market data handling
├── rust_client/
│   ├── Cargo.toml            
│   └── src/
│       ├── lib.rs            
│       └── kraken_api.rs 
├── data/
│   └── historical/ (or logs/, if storing logs here)
├── logs/
│   └── trade_log.txt
├── models/
│   └── strategy_model.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── trader.py
│   ├── kraken_api.py
│   ├── config_load.py
│   ├── apps/
│   │   ├── data-collector/
│   │   ├── execution/
│   │   ├── paper-trader/
│   │   ├── portfolio-manager/
│   │   └── strategies/
│   │       └── market_maker.py    # Market making strategy
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── kraken_python_client.py
│   │   └── kraken_sync_client.py
│   ├── utils/
│   │   ├── helpers.py
│   │   ├── plotter.py
│   │   └── account_tools.py
├── tests/
│   ├── test_strategy.py
│   ├── test_api.py
│   ├── test_kraken_client.py
│   └── test_rust_client.py
└── docs/
    └── architecture.md
```
---
## Python-Rust Integration
TradeByte leverages the power of Rust for performance-critical operations, like interacting with the Kraken API, while Python is used for higher-level strategy development, backtesting, and other logic. This integration combines the best of both languages: Rust for speed and Python for flexibility.

### Rust Functions in Python
Rust functions are exposed to Python via `maturin`, which allows you to build and package Rust extensions into Python modules. For example, functions like `get_bid()` and `get_ask()` retrieve real-time market data from Kraken using Rust's speed.
* `get_bid()` Fetches the current bid price for the selected trading pair.
* `get_ask()` Fetches the current ask price for the selected trading pair.

### Building the Rust Extension
To build the Rust extension and make it available for Python, use the following command:
```bash
maturin develop
```

### Example
```python
from rust_kraken_client import get_bid, get_ask

def test_rust_integration():
    print("Bid price:", get_bid())  # Call the Rust function to get the bid
    print("Ask price:", get_ask())  # Call the Rust function to get the ask

if __name__ == "__main__":
    test_rust_integration()
```

### Managing Kraken API Requests
Rust handles the Kraken API requests efficiently. When you call functions like `get_bid()` or `get_ask()`, they internally handle API requests, error handling, and response parsing, ensuring high performance.

---

## Market Making Strategy

The market making strategy (`src/apps/strategies/market_maker.py`) is a sophisticated automated trading system that:

- **Maintains Order Books**: Continuously places and manages buy/sell orders
- **Dynamic Pricing**: Adjusts prices based on market conditions and reference prices
- **Risk Management**: Implements position sizing and order limits
- **Automatic Recovery**: Restarts automatically if connections are lost
- **Efficient Updates**: Uses order editing when possible to minimize API calls

### Key Features:
- **Fixed Ladder Size**: 5 orders per side for consistent market making
- **Order Editing**: Efficiently updates existing orders instead of canceling/replacing
- **Connection Recovery**: Automatic restart on connection loss
- **Real-time Updates**: Processes order book updates in real-time

---

## Contributing
Follow https://opensource.guide/

---
## Troubleshooting

### Common Issues

1. **WebSocket Connection Errors**: The system now automatically restarts on connection loss
2. **Order Placement Failures**: Check your API permissions and account balance
3. **Rust Build Issues**: Ensure you have the latest version of `maturin` installed

### Recent Fixes
- Fixed WebSocket connection state checking
- Improved message format handling for Kraken WebSocket API
- Enhanced error handling and logging
- Added automatic restart capabilities for market maker strategy

---

