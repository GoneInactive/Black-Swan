# tests/test_strategy.py

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategy.sma import SMAStrategy
from strategy.rsi import RSIStrategy

# Sample OHLC data
def generate_sample_data():
    data = {
        "timestamp": pd.date_range(start="2024-01-01", periods=50, freq="H"),
        "open": pd.Series([100 + i + (i % 5) for i in range(50)]),
        "high": pd.Series([102 + i for i in range(50)]),
        "low": pd.Series([98 + i for i in range(50)]),
        "close": pd.Series([100 + i for i in range(50)]),
        "volume": pd.Series([10 + i*0.5 for i in range(50)]),
    }
    return pd.DataFrame(data)

def test_sma_strategy():
    print("\n🔍 Testing SMA Strategy")
    df = generate_sample_data()
    strat = SMAStrategy(short_window=5, long_window=10)
    result = strat.generate_signals(df)

    assert "signal" in result.columns, "SMA strategy did not generate 'signal' column"
    print(result[['timestamp', 'close', 'signal']].tail())

def test_rsi_strategy():
    print("\n🔍 Testing RSI Strategy")
    df = generate_sample_data()
    strat = RSIStrategy(period=14, overbought=70, oversold=30)
    result = strat.generate_signals(df)

    assert "signal" in result.columns, "RSI strategy did not generate 'signal' column"
    assert "rsi" in result.columns, "RSI strategy did not compute 'rsi' column"
    print(result[['timestamp', 'close', 'rsi', 'signal']].tail())

if __name__ == "__main__":
    test_sma_strategy()
    test_rsi_strategy()


'''
python tests/test_strategy.py
'''