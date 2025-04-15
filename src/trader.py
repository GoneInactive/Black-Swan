# src/trader.py

import time
import logging
from kraken_api import KrakenClient
from strategy.sma import SMAStrategy
from helpers import log_trade, is_trade_allowed, save_data, load_data

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Trader:
    def __init__(self, config):
        self.config = config
        self.kraken_client = KrakenClient(
            api_key=config['kraken']['api_key'],
            api_secret=config['kraken']['api_secret']
        )
        self.strategy = SMAStrategy(
            short_window=config['strategy']['parameters']['short_window'],
            long_window=config['strategy']['parameters']['long_window']
        )
        self.balance = 0
        self.symbol = f"{config['trade']['base_asset']}Z{config['trade']['quote_asset']}"
        self.order_size = config['trade']['order_size']
        self.paper_trading = config['trade']['paper_trading']

    def get_balance(self):
        """Fetch current balance"""
        balance_info = self.kraken_client.get_balance()
        self.balance = float(balance_info.get(self.config['trade']['quote_asset'], 0))
        logger.info(f"Current balance: {self.balance} {self.config['trade']['quote_asset']}")
        return self.balance

    def get_market_data(self):
        """Get the latest market data (OHLC)"""
        df = self.kraken_client.get_ohlc(pair=self.symbol, interval=60)  # 1-hour candles
        return df

    def execute_trade(self, action, price):
        """Execute a trade action (buy/sell)"""
        if self.paper_trading:
            logger.info(f"[Paper Trading] {action.capitalize()} order for {self.order_size} at ${price:.2f}")
        else:
            # Place live order
            response = self.kraken_client.place_order(
                pair=self.symbol,
                side=action,
                volume=self.order_size
            )
            if response:
                log_trade(action, price, self.order_size)

    def run(self):
        """Main trading loop"""
        while True:
            logger.info("Fetching market data...")
            df = self.get_market_data()
            if df is None:
                logger.error("Failed to fetch market data. Retrying...")
                time.sleep(60)
                continue

            df = self.strategy.generate_signals(df)
            last_signal = df['signal'].iloc[-1]
            last_price = df['close'].iloc[-1]

            logger.info(f"Signal: {last_signal}, Price: {last_price:.2f}")

            if last_signal == 1:  # Buy signal
                self.get_balance()
                if is_trade_allowed(self.balance, last_price, self.order_size):
                    self.execute_trade('buy', last_price)
                else:
                    logger.warning("Insufficient balance for buy order.")

            elif last_signal == -1:  # Sell signal
                self.get_balance()
                if is_trade_allowed(self.balance, last_price, self.order_size):
                    self.execute_trade('sell', last_price)
                else:
                    logger.warning("Insufficient balance for sell order.")
            
            time.sleep(60)  # Wait before the next check (1 minute)

if __name__ == "__main__":
    import yaml

    # Load configuration
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Initialize and start the trader
    trader = Trader(config)
    trader.run()


'''
 Explanation of the Trader Class:

    __init__: Initializes the trader with configuration, Kraken client, and strategy.

    get_balance: Fetches the available balance in your quote asset (e.g., USD).

    get_market_data: Fetches OHLC data from Kraken for the selected trading pair (e.g., BTC/USD).

    execute_trade: Executes a buy or sell trade, depending on the signal. If paper trading is enabled, it simulates the trade. Otherwise, it places a real order on Kraken.

    run: The main trading loop that:

        Fetches market data.

        Passes the data to the SMA strategy to get buy/sell/hold signals.

        Executes trades based on the signals.

        Waits for the next iteration (60 seconds in this case).
'''