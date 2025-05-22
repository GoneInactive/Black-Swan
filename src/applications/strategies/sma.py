# src/strategy/sma.py

import pandas as pd

class SMAStrategy:
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, df):
        """
        Expects a DataFrame with a 'close' column.
        Returns a DataFrame with 'signal' column: 1 for buy, -1 for sell, 0 for hold.
        """
        df = df.copy()
        df['sma_short'] = df['close'].rolling(window=self.short_window).mean()
        df['sma_long'] = df['close'].rolling(window=self.long_window).mean()

        df['signal'] = 0
        df['signal'][self.short_window:] = (
            (df['sma_short'][self.short_window:] > df['sma_long'][self.short_window:]).astype(int)
            - (df['sma_short'][self.short_window:] < df['sma_long'][self.short_window:]).astype(int)
        )
        return df
