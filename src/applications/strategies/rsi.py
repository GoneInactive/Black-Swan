# src/strategy/rsi.py

import pandas as pd

class RSIStrategy:
    def __init__(self, period=14, overbought=70, oversold=30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def calculate_rsi(self, df):
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=self.period, min_periods=self.period).mean()
        avg_loss = loss.rolling(window=self.period, min_periods=self.period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signals(self, df):
        df = df.copy()
        df['rsi'] = self.calculate_rsi(df)

        df['signal'] = 0
        df.loc[df['rsi'] < self.oversold, 'signal'] = 1   # Buy
        df.loc[df['rsi'] > self.overbought, 'signal'] = -1  # Sell

        return df

'''
Example usage in main.py:


from strategy.rsi import RSIStrategy

strat = RSIStrategy(
    period=config['strategy']['parameters']['period'],
    overbought=config['strategy']['parameters']['overbought'],
    oversold=config['strategy']['parameters']['oversold']
)
'''