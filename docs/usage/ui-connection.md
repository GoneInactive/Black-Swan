# UI Connection Documentation

## Overview

TradeByte provides multiple user interface options for interacting with the trading platform:

1. **Streamlit Web Interface** - Browser-based dashboard
2. **PyQt6 Desktop Application** - Native desktop interface
3. **Terminal Interface** - Command-line interface
4. **API Endpoints** - REST API for custom integrations

## Streamlit Web Interface

### Setup and Configuration

```python
# ui/app.py
import streamlit as st
import plotly.graph_objects as go
import json
import pandas as pd
from pathlib import Path

def load_market_data():
    """Load market data from JSON files"""
    data_dir = Path("ui/data")
    data = {}
    
    for file in data_dir.glob("*_prices.json"):
        with open(file, 'r') as f:
            data[file.stem.replace('_prices', '')] = json.load(f)
    
    return data

def create_price_chart(data, symbol):
    """Create interactive price chart using Plotly"""
    df = pd.DataFrame(data[symbol])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['close'],
        mode='lines',
        name=f'{symbol.upper()} Price'
    ))
    
    fig.update_layout(
        title=f'{symbol.upper()} Price Chart',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        height=400
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="TradeByte Dashboard",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("TradeByte Trading Dashboard")
    
    # Load data
    market_data = load_market_data()
    
    # Sidebar for controls
    st.sidebar.header("Controls")
    selected_symbol = st.sidebar.selectbox(
        "Select Symbol",
        list(market_data.keys())
    )
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Price Chart")
        chart = create_price_chart(market_data, selected_symbol)
        st.plotly_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Market Data")
        if selected_symbol in market_data:
            latest_data = market_data[selected_symbol][-1]
            st.metric("Current Price", f"${latest_data['close']:.2f}")
            st.metric("24h Change", f"{latest_data.get('change_24h', 0):.2f}%")
            st.metric("Volume", f"{latest_data.get('volume', 0):.0f}")
    
    # Strategy status
    st.subheader("Strategy Status")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("Active Strategies", "2")
    
    with status_col2:
        st.metric("Total P&L", "$1,234.56")
    
    with status_col3:
        st.metric("Open Orders", "10")

if __name__ == "__main__":
    main()
```

### Running the Streamlit App

```bash
# Install Streamlit if not already installed
pip install streamlit

# Run the app
streamlit run ui/app.py
```

### Auto-refresh Configuration

```python
# ui/app.py with auto-refresh
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 30 seconds
count = st_autorefresh(interval=30000, limit=None, key="fizzbuzzcounter")

# Your existing code here...
```

## PyQt6 Desktop Application

### Main Application Structure

```python
# ui/desktop_app.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QLabel, QPushButton, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import json
import requests

class DataWorker(QThread):
    """Background thread for data updates"""
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        while self.running:
            try:
                # Fetch data from backend
                response = requests.get('http://localhost:5000/api/prices')
                if response.status_code == 200:
                    data = response.json()
                    self.data_updated.emit(data)
            except Exception as e:
                print(f"Error fetching data: {e}")
            
            self.msleep(5000)  # Update every 5 seconds
    
    def stop(self):
        self.running = False

class TradeByteDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_data_worker()
    
    def init_ui(self):
        self.setWindowTitle("TradeByte Desktop")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("TradeByte Trading Platform")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Strategy")
        self.start_button.clicked.connect(self.start_strategy)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Strategy")
        self.stop_button.clicked.connect(self.stop_strategy)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels([
            "Symbol", "Price", "Change", "Volume"
        ])
        layout.addWidget(self.data_table)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def init_data_worker(self):
        self.data_worker = DataWorker()
        self.data_worker.data_updated.connect(self.update_data)
        self.data_worker.start()
    
    def start_strategy(self):
        try:
            response = requests.post('http://localhost:5000/api/execute', 
                                   json={'command': 'start_market_maker'})
            if response.status_code == 200:
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.statusBar().showMessage("Strategy started")
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}")
    
    def stop_strategy(self):
        try:
            response = requests.post('http://localhost:5000/api/execute', 
                                   json={'command': 'stop_market_maker'})
            if response.status_code == 200:
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.statusBar().showMessage("Strategy stopped")
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}")
    
    def update_data(self, data):
        """Update the data table with new market data"""
        self.data_table.setRowCount(len(data))
        
        for i, (symbol, info) in enumerate(data.items()):
            self.data_table.setItem(i, 0, QTableWidgetItem(symbol.upper()))
            self.data_table.setItem(i, 1, QTableWidgetItem(f"${info['price']:.2f}"))
            self.data_table.setItem(i, 2, QTableWidgetItem(f"{info['change']:.2f}%"))
            self.data_table.setItem(i, 3, QTableWidgetItem(f"{info['volume']:.0f}"))
    
    def closeEvent(self, event):
        self.data_worker.stop()
        self.data_worker.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = TradeByteDesktop()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## Terminal Interface

### Command-Line Interface

```python
# ui/terminal/terminal_ui.py
import cmd
import asyncio
import json
from pathlib import Path
from src.apps.strategies.market_maker import MarketMaker

class TradeByteTerminal(cmd.Cmd):
    intro = 'Welcome to TradeByte Terminal. Type help or ? to list commands.\n'
    prompt = '(tradebyte) '
    
    def __init__(self):
        super().__init__()
        self.strategy = None
        self.running = False
    
    def do_start(self, arg):
        """Start the market maker strategy"""
        if not self.running:
            try:
                self.strategy = MarketMaker()
                asyncio.create_task(self.strategy.start())
                self.running = True
                print("Market maker strategy started")
            except Exception as e:
                print(f"Error starting strategy: {e}")
        else:
            print("Strategy is already running")
    
    def do_stop(self, arg):
        """Stop the market maker strategy"""
        if self.running and self.strategy:
            try:
                asyncio.create_task(self.strategy.stop())
                self.running = False
                print("Market maker strategy stopped")
            except Exception as e:
                print(f"Error stopping strategy: {e}")
        else:
            print("No strategy is running")
    
    def do_status(self, arg):
        """Show current status"""
        if self.running:
            print("Strategy Status: RUNNING")
            if self.strategy:
                print(f"Trading Pair: {self.strategy.pair}")
                print(f"Buy Orders: {len(self.strategy.buy_orders['txid'])}")
                print(f"Sell Orders: {len(self.strategy.sell_orders['txid'])}")
        else:
            print("Strategy Status: STOPPED")
    
    def do_prices(self, arg):
        """Show current market prices"""
        try:
            data_dir = Path("ui/data")
            for file in data_dir.glob("*_prices.json"):
                with open(file, 'r') as f:
                    data = json.load(f)
                    if data:
                        symbol = file.stem.replace('_prices', '').upper()
                        latest = data[-1]
                        print(f"{symbol}: ${latest['close']:.2f}")
        except Exception as e:
            print(f"Error loading prices: {e}")
    
    def do_config(self, arg):
        """Show current configuration"""
        try:
            with open("config/config.yaml", 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                print("Current Configuration:")
                print(json.dumps(config, indent=2, default=str))
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def do_quit(self, arg):
        """Exit the terminal"""
        if self.running:
            print("Stopping strategy before exit...")
            asyncio.create_task(self.strategy.stop())
        print("Goodbye!")
        return True
    
    def do_exit(self, arg):
        """Exit the terminal"""
        return self.do_quit(arg)

def main():
    terminal = TradeByteTerminal()
    try:
        terminal.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
        if terminal.running:
            asyncio.create_task(terminal.strategy.stop())

if __name__ == "__main__":
    main()
```

## Backend API Server

### Flask API Server

```python
# ui/api_server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import subprocess
import asyncio
from pathlib import Path
import yaml

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

class StrategyManager:
    def __init__(self):
        self.running_strategies = {}
    
    def start_market_maker(self):
        """Start the market maker strategy"""
        try:
            process = subprocess.Popen([
                'python', 'src/apps/strategies/market_maker.py'
            ])
            self.running_strategies['market_maker'] = process
            return True
        except Exception as e:
            print(f"Error starting market maker: {e}")
            return False
    
    def stop_market_maker(self):
        """Stop the market maker strategy"""
        if 'market_maker' in self.running_strategies:
            process = self.running_strategies['market_maker']
            process.terminate()
            del self.running_strategies['market_maker']
            return True
        return False

strategy_manager = StrategyManager()

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get current market prices"""
    try:
        data_dir = Path("ui/data")
        prices = {}
        
        for file in data_dir.glob("*_prices.json"):
            with open(file, 'r') as f:
                data = json.load(f)
                if data:
                    symbol = file.stem.replace('_prices', '')
                    latest = data[-1]
                    prices[symbol] = {
                        'price': latest['close'],
                        'change': latest.get('change_24h', 0),
                        'volume': latest.get('volume', 0)
                    }
        
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute trading commands"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        if command == 'start_market_maker':
            success = strategy_manager.start_market_maker()
            return jsonify({'success': success})
        
        elif command == 'stop_market_maker':
            success = strategy_manager.stop_market_maker()
            return jsonify({'success': success})
        
        else:
            return jsonify({'error': 'Unknown command'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        with open("config/config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        new_config = request.get_json()
        with open("config/config.yaml", 'w') as f:
            yaml.dump(new_config, f, default_flow_style=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        status = {
            'strategies': {
                'market_maker': 'market_maker' in strategy_manager.running_strategies
            },
            'connections': {
                'websocket': True,  # You can add actual connection checking here
                'api': True
            }
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## Data Flow Between UI and Backend

### Real-time Data Flow

```
┌─────────────┐    WebSocket    ┌─────────────┐    HTTP API    ┌─────────────┐
│   Kraken    │ ──────────────► │   Backend   │ ─────────────► │    Frontend │
│   Exchange  │                 │   (Python)  │                │   (UI)      │
└─────────────┘                 └─────────────┘                └─────────────┘
                                       │                              │
                                       ▼                              ▼
                                ┌─────────────┐                ┌─────────────┐
                                │   Data      │                │   Display   │
                                │   Storage   │                │   Updates   │
                                │   (JSON)    │                │   (Real-time)│
                                └─────────────┘                └─────────────┘
```

### Command Flow

```
┌─────────────┐    User Input   ┌─────────────┐    API Call    ┌─────────────┐
│    User     │ ──────────────► │   Frontend  │ ─────────────► │   Backend   │
│  Interface  │                 │   (UI)      │                │   (Python)  │
└─────────────┘                 └─────────────┘                └─────────────┘
                                                                      │
                                                                      ▼
                                                               ┌─────────────┐
                                                               │   Strategy  │
                                                               │  Execution  │
                                                               └─────────────┘
                                                                      │
                                                                      ▼
                                                               ┌─────────────┐
                                                               │   Kraken    │
                                                               │    API      │
                                                               └─────────────┘
```

## Configuration for Different UI Types

### Streamlit Configuration

```python
# ui/streamlit_config.py
import streamlit as st

def configure_streamlit():
    st.set_page_config(
        page_title="TradeByte Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    st.sidebar.title("TradeByte Controls")
    
    # Strategy controls
    st.sidebar.subheader("Strategy Management")
    if st.sidebar.button("Start Market Maker"):
        # API call to start strategy
        pass
    
    if st.sidebar.button("Stop Market Maker"):
        # API call to stop strategy
        pass
    
    # Configuration
    st.sidebar.subheader("Configuration")
    selected_pair = st.sidebar.selectbox(
        "Trading Pair",
        ["BTC/USD", "ETH/USD", "ADA/USD"]
    )
    
    return selected_pair
```

### PyQt6 Configuration

```python
# ui/qt_config.py
from PyQt6.QtWidgets import QStyleFactory
from PyQt6.QtCore import Qt

def configure_qt_app(app):
    """Configure PyQt6 application appearance"""
    # Set application style
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Set application properties
    app.setApplicationName("TradeByte")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TradeByte")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

def create_dark_theme():
    """Create dark theme for the application"""
    return """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QPushButton {
        background-color: #404040;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
    }
    QPushButton:hover {
        background-color: #505050;
    }
    QPushButton:pressed {
        background-color: #303030;
    }
    QTableWidget {
        background-color: #3b3b3b;
        gridline-color: #555555;
        color: #ffffff;
    }
    QHeaderView::section {
        background-color: #404040;
        color: #ffffff;
        padding: 4px;
        border: 1px solid #555555;
    }
    """
```

## Error Handling and Logging

### UI Error Handling

```python
# ui/error_handling.py
import logging
from functools import wraps
import streamlit as st

def handle_ui_errors(func):
    """Decorator for handling UI errors gracefully"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"UI Error in {func.__name__}: {e}")
            
            # For Streamlit
            if 'streamlit' in str(type(st)):
                st.error(f"An error occurred: {str(e)}")
            
            # For PyQt6
            elif 'PyQt6' in str(type(e)):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
            
            return None
    return wrapper

class UILogger:
    """Centralized logging for UI components"""
    
    def __init__(self, name="tradebyte_ui"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler('logs/ui.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.setLevel(logging.INFO)
    
    def log_user_action(self, action, details=None):
        """Log user actions"""
        message = f"User action: {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_error(self, error, context=None):
        """Log errors with context"""
        message = f"Error: {error}"
        if context:
            message += f" - Context: {context}"
        self.logger.error(message)
```

This comprehensive UI connection documentation covers all the different ways to interact with the TradeByte platform, from web interfaces to desktop applications and command-line tools. Each interface type is designed to provide a seamless user experience while maintaining the performance and reliability of the underlying trading system.
