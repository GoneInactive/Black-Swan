# src/main.py

import yaml
import pandas as pd
from strategies.sma import SMAStrategy

def load_config(path='config/config.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_historical_data(symbol='BTC/USD', interval='1h', start=None, end=None):
    # Stub: replace with Kraken API call or data loader
    df = pd.read_csv('data/BTCUSD_1h.csv')  # Example file
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def run_backtest(strategy, df, starting_balance=10000, order_size=0.001):
    df = strategy.generate_signals(df)
    balance = starting_balance
    position = 0
    for _, row in df.iterrows():
        if row['signal'] == 1 and balance >= row['close'] * order_size:
            position += order_size
            balance -= row['close'] * order_size
        elif row['signal'] == -1 and position >= order_size:
            position -= order_size
            balance += row['close'] * order_size
    value = balance + position * df['close'].iloc[-1]
    print(f"Final portfolio value: ${value:.2f}")

def main():
    config = load_config()

    if config['strategy']['name'] == 'sma':
        strat = SMAStrategy(
            short_window=config['strategy']['parameters']['short_window'],
            long_window=config['strategy']['parameters']['long_window']
        )
    else:
        raise ValueError("Unknown strategy")

    df = get_historical_data()
    run_backtest(
        strat,
        df,
        starting_balance=config['backtest']['initial_balance'],
        order_size=config['trade']['order_size']
    )

if __name__ == "__main__":
    main()
