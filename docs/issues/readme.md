# Known Issues and Troubleshooting

## Table of Contents
1. [WebSocket Connection Issues](#websocket-connection-issues)
2. [API Authentication Problems](#api-authentication-problems)
3. [Strategy Execution Issues](#strategy-execution-issues)
4. [Performance Issues](#performance-issues)
5. [UI/Interface Problems](#uiinterface-problems)
6. [Rust Integration Issues](#rust-integration-issues)
7. [Configuration Problems](#configuration-problems)
8. [Data Collection Issues](#data-collection-issues)

## WebSocket Connection Issues

### Issue: Connection Lost Errors
**Symptoms:**
- `WebSocket connection lost. Exiting run loop.`
- `ConnectionClosed` exceptions
- Strategy stops unexpectedly

**Causes:**
- Network instability
- Kraken API rate limiting
- Firewall blocking WebSocket connections
- Incorrect WebSocket URL

**Solutions:**
1. **Automatic Restart**: The market maker strategy now automatically restarts on connection loss
2. **Check Network**: Ensure stable internet connection
3. **Firewall Settings**: Allow WebSocket connections on port 443
4. **Rate Limiting**: Implement exponential backoff for reconnection attempts

```python
# Example: Enhanced connection handling
class RobustWebSocketClient:
    def __init__(self, max_retries=5, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_count = 0
    
    async def connect_with_retry(self):
        while self.retry_count < self.max_retries:
            try:
                await self.connect()
                self.retry_count = 0  # Reset on successful connection
                break
            except Exception as e:
                self.retry_count += 1
                wait_time = self.backoff_factor ** self.retry_count
                logger.warning(f"Connection failed, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
```

### Issue: Message Format Errors
**Symptoms:**
- `'dict' object has no attribute 'split'`
- JSON decode errors
- Unexpected message format

**Causes:**
- Kraken API changes message format
- Different WebSocket API versions
- Malformed messages

**Solutions:**
1. **Enhanced Message Handling**: Updated message parser to handle different formats
2. **Version Detection**: Check API version and adjust parsing accordingly
3. **Error Logging**: Improved error logging for debugging

```python
# Fixed message handling
async def _handle_public_message(self, message: str):
    try:
        data = json.loads(message)
        
        if isinstance(data, dict) and 'event' in data:
            logger.debug(f"Received event message: {data}")
            return

        if isinstance(data, list) and len(data) >= 3:
            channel_info = data[2]
            
            # Handle different channel info formats
            if isinstance(channel_info, str):
                channel_name = channel_info.split('-')[0]
            elif isinstance(channel_info, dict) and 'name' in channel_info:
                channel_name = channel_info['name']
            else:
                logger.warning(f"Unexpected channel info format: {channel_info}")
                return
            
            # Process message...
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode WebSocket message: {e}")
    except Exception as e:
        logger.error(f"Error handling public message: {e}")
```

## API Authentication Problems

### Issue: Invalid API Key
**Symptoms:**
- `API key and secret are required for account operations`
- `Failed to get WebSocket token`
- 401 Unauthorized errors

**Causes:**
- Missing or incorrect API credentials
- API key doesn't have required permissions
- API key expired or revoked

**Solutions:**
1. **Check Configuration**: Verify `config/config.yaml` has correct credentials
2. **API Permissions**: Ensure API key has required permissions:
   - View account data
   - View open orders and trades
   - Place and cancel orders
   - Query funds
3. **Environment Variables**: Use environment variables for sensitive data

```yaml
# config/config.yaml
kraken:
  api_key: "${KRAKEN_API_KEY}"  # Use environment variable
  api_secret: "${KRAKEN_API_SECRET}"
  sandbox: false  # Set to true for testing
```

### Issue: Rate Limiting
**Symptoms:**
- `Rate limit exceeded` errors
- Requests being throttled
- Strategy performance degradation

**Causes:**
- Too many API requests per second
- Exceeding Kraken's rate limits
- Inefficient request patterns

**Solutions:**
1. **Request Throttling**: Implement delays between requests
2. **Batch Requests**: Group multiple operations when possible
3. **WebSocket Usage**: Use WebSocket for real-time data instead of REST API

```python
# Rate limiting implementation
import asyncio
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests=15, time_window=1):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    async def acquire(self):
        now = time.time()
        
        # Remove old requests
        while self.requests and now - self.requests[0] > self.time_window:
            self.requests.popleft()
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0])
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)
```

## Strategy Execution Issues

### Issue: Order Placement Failures
**Symptoms:**
- Orders not being placed
- `Failed to place order` errors
- Strategy not executing trades

**Causes:**
- Insufficient funds
- Invalid order parameters
- Market closed or suspended
- Price outside allowed range

**Solutions:**
1. **Balance Checking**: Verify sufficient funds before placing orders
2. **Order Validation**: Validate order parameters before submission
3. **Error Handling**: Implement proper error handling and logging

```python
async def place_order_with_validation(self, pair, side, volume, price):
    try:
        # Check balance
        balance = await self.get_balance()
        if side == 'buy':
            required = float(volume) * float(price)
            if balance['USD'] < required:
                logger.error(f"Insufficient USD balance: {balance['USD']} < {required}")
                return False
        
        # Validate order parameters
        if float(volume) < self.min_order:
            logger.error(f"Order too small: {volume} < {self.min_order}")
            return False
        
        # Place order
        response = await self.client.account.add_order(
            pair=pair,
            type=side,
            ordertype='limit',
            volume=str(volume),
            price=str(price)
        )
        
        if response.get('status') == 'ok':
            logger.info(f"Order placed successfully: {response}")
            return True
        else:
            logger.error(f"Order placement failed: {response}")
            return False
            
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return False
```

### Issue: Strategy Not Responding to Market Changes
**Symptoms:**
- Orders not updating when market moves
- Strategy appears "frozen"
- No new orders being placed

**Causes:**
- WebSocket connection issues
- Order book not updating
- Strategy logic errors
- Performance bottlenecks

**Solutions:**
1. **Connection Monitoring**: Monitor WebSocket connection status
2. **Order Book Validation**: Verify order book data is current
3. **Performance Optimization**: Optimize strategy execution

```python
class MarketMakerMonitor:
    def __init__(self):
        self.last_update = time.time()
        self.update_threshold = 30  # 30 seconds
    
    def check_responsiveness(self):
        """Check if strategy is responding to market updates"""
        current_time = time.time()
        time_since_update = current_time - self.last_update
        
        if time_since_update > self.update_threshold:
            logger.warning(f"Strategy not responding for {time_since_update}s")
            return False
        
        return True
    
    def update_timestamp(self):
        """Update the last update timestamp"""
        self.last_update = time.time()
```

## Performance Issues

### Issue: High Latency
**Symptoms:**
- Slow order execution
- Delayed market data
- Poor strategy performance

**Causes:**
- Network latency
- Inefficient code
- Resource constraints
- Database bottlenecks

**Solutions:**
1. **Use Rust Components**: Leverage Rust for performance-critical operations
2. **Optimize WebSocket**: Minimize WebSocket message processing time
3. **Connection Optimization**: Use low-latency connections

```python
# Performance monitoring
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.operation_times = []
    
    def measure_operation(self, operation_name):
        """Decorator to measure operation performance"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start = time.time()
                result = await func(*args, **kwargs)
                duration = time.time() - start
                
                self.operation_times.append({
                    'operation': operation_name,
                    'duration': duration,
                    'timestamp': time.time()
                })
                
                if duration > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation: {operation_name} took {duration:.3f}s")
                
                return result
            return wrapper
        return decorator
    
    def get_performance_stats(self):
        """Get performance statistics"""
        if not self.operation_times:
            return {}
        
        durations = [op['duration'] for op in self.operation_times]
        return {
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'total_operations': len(self.operation_times)
        }
```

### Issue: Memory Leaks
**Symptoms:**
- Increasing memory usage over time
- Application crashes
- Poor performance after running for extended periods

**Causes:**
- Unclosed connections
- Accumulating data structures
- Resource not properly released

**Solutions:**
1. **Resource Management**: Ensure proper cleanup of resources
2. **Memory Monitoring**: Monitor memory usage
3. **Garbage Collection**: Force garbage collection when needed

```python
import gc
import psutil
import os

class MemoryManager:
    def __init__(self, memory_threshold=0.8):  # 80% memory usage threshold
        self.memory_threshold = memory_threshold
        self.process = psutil.Process(os.getpid())
    
    def check_memory_usage(self):
        """Check current memory usage"""
        memory_percent = self.process.memory_percent()
        
        if memory_percent > self.memory_threshold:
            logger.warning(f"High memory usage: {memory_percent:.1f}%")
            self.cleanup_memory()
        
        return memory_percent
    
    def cleanup_memory(self):
        """Clean up memory"""
        # Force garbage collection
        gc.collect()
        
        # Clear any cached data
        # This depends on your specific implementation
        
        logger.info("Memory cleanup completed")
    
    def get_memory_info(self):
        """Get detailed memory information"""
        memory_info = self.process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': self.process.memory_percent()
        }
```

## UI/Interface Problems

### Issue: Streamlit App Not Loading
**Symptoms:**
- Streamlit app shows error page
- Data not displaying
- Interface unresponsive

**Causes:**
- Missing dependencies
- Incorrect file paths
- Port conflicts
- Data file issues

**Solutions:**
1. **Check Dependencies**: Ensure all required packages are installed
2. **Verify File Paths**: Check that data files exist and are accessible
3. **Port Configuration**: Use different port if default is occupied

```bash
# Install missing dependencies
pip install streamlit plotly streamlit-autorefresh

# Run on different port
streamlit run ui/app.py --server.port 8501

# Check for port conflicts
netstat -an | grep 8501
```

### Issue: PyQt6 Application Crashes
**Symptoms:**
- Application crashes on startup
- GUI elements not displaying
- Thread-related errors

**Causes:**
- Missing PyQt6 dependencies
- Thread safety issues
- Resource conflicts

**Solutions:**
1. **Install Dependencies**: Ensure PyQt6 is properly installed
2. **Thread Safety**: Use proper thread synchronization
3. **Error Handling**: Add comprehensive error handling

```python
# PyQt6 thread safety
from PyQt6.QtCore import QThread, pyqtSignal, QMutex

class SafeWorker(QThread):
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.running = True
    
    def run(self):
        try:
            while self.running:
                # Your work here
                data = self.fetch_data()
                self.data_ready.emit(data)
                self.msleep(1000)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        self.mutex.lock()
        self.running = False
        self.mutex.unlock()
```

## Rust Integration Issues

### Issue: Rust Module Not Building
**Symptoms:**
- `maturin develop` fails
- Import errors for Rust modules
- Build errors

**Causes:**
- Missing Rust toolchain
- Incorrect PyO3 version
- Build environment issues

**Solutions:**
1. **Install Rust**: Ensure Rust is properly installed
2. **Update Dependencies**: Update PyO3 and maturin
3. **Environment Variables**: Set required environment variables

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install maturin
pip install maturin

# Set environment variable for compatibility
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Build Rust module
cd rust_client
maturin develop
```

### Issue: Rust-Python Communication Errors
**Symptoms:**
- `ModuleNotFoundError` for Rust modules
- Data type conversion errors
- Performance not improved

**Causes:**
- Incorrect module imports
- Data type mismatches
- Build configuration issues

**Solutions:**
1. **Check Imports**: Verify correct import statements
2. **Data Types**: Ensure proper data type handling
3. **Performance Testing**: Benchmark Rust vs Python performance

```python
# Correct Rust module import
try:
    from rust_client import get_bid, get_ask
except ImportError as e:
    logger.error(f"Failed to import Rust modules: {e}")
    logger.info("Falling back to Python implementation")
    # Fallback to Python implementation
```

## Configuration Problems

### Issue: Configuration Not Loading
**Symptoms:**
- Default values being used
- Configuration errors
- Strategy not using custom settings

**Causes:**
- Missing config file
- Incorrect YAML syntax
- File permissions

**Solutions:**
1. **File Validation**: Check config file exists and is readable
2. **YAML Syntax**: Validate YAML syntax
3. **Default Values**: Provide sensible defaults

```python
import yaml
from pathlib import Path

def load_config(config_path="config/config.yaml"):
    """Load configuration with error handling"""
    try:
        config_file = Path(config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}")
            return get_default_config()
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['kraken', 'trading']
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required config field: {field}")
                return get_default_config()
        
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"YAML syntax error: {e}")
        return get_default_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()

def get_default_config():
    """Return default configuration"""
    return {
        'kraken': {
            'api_key': '',
            'api_secret': '',
            'sandbox': True
        },
        'trading': {
            'default_pair': 'BTC/USD',
            'max_position_size': 1000,
            'min_order_size': 10
        }
    }
```

## Data Collection Issues

### Issue: Market Data Not Updating
**Symptoms:**
- Stale market data
- No new price updates
- Data collection stopped

**Causes:**
- WebSocket connection issues
- Data processing errors
- Storage problems

**Solutions:**
1. **Connection Monitoring**: Monitor WebSocket connections
2. **Data Validation**: Validate incoming data
3. **Storage Management**: Ensure proper data storage

```python
class DataCollectionMonitor:
    def __init__(self):
        self.last_update = {}
        self.update_threshold = 60  # 60 seconds
    
    def check_data_freshness(self, symbol):
        """Check if data is fresh for a symbol"""
        current_time = time.time()
        last_update = self.last_update.get(symbol, 0)
        
        if current_time - last_update > self.update_threshold:
            logger.warning(f"Data stale for {symbol}: {current_time - last_update}s old")
            return False
        
        return True
    
    def update_timestamp(self, symbol):
        """Update timestamp for symbol"""
        self.last_update[symbol] = time.time()
    
    def get_stale_symbols(self):
        """Get list of symbols with stale data"""
        current_time = time.time()
        stale_symbols = []
        
        for symbol, last_update in self.last_update.items():
            if current_time - last_update > self.update_threshold:
                stale_symbols.append(symbol)
        
        return stale_symbols
```

## General Troubleshooting Steps

### 1. Check Logs
Always check the logs first for error messages and warnings:

```bash
# Check application logs
tail -f logs/tradebyte.log

# Check system logs
journalctl -u tradebyte -f
```

### 2. Verify Configuration
Ensure all configuration files are correct:

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Check file permissions
ls -la config/
```

### 3. Test Connectivity
Verify network connectivity and API access:

```python
import requests

def test_kraken_api():
    try:
        response = requests.get('https://api.kraken.com/0/public/Time')
        if response.status_code == 200:
            print("Kraken API is accessible")
            return True
        else:
            print(f"Kraken API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False
```

### 4. Monitor Resources
Check system resources for bottlenecks:

```python
import psutil

def check_system_resources():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    
    print(f"CPU: {cpu_percent}%")
    print(f"Memory: {memory_percent}%")
    print(f"Disk: {disk_usage}%")
    
    if cpu_percent > 80 or memory_percent > 80:
        print("Warning: High resource usage detected")
```

### 5. Restart Services
When in doubt, restart the application:

```bash
# Stop the application
pkill -f market_maker.py

# Clear any temporary files
rm -rf /tmp/tradebyte_*

# Restart the application
python src/apps/strategies/market_maker.py
```

This comprehensive troubleshooting guide should help resolve most issues encountered with the TradeByte platform. Always check the logs first and follow the systematic approach outlined above.
