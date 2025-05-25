from rust_kraken_client import get_bid, get_ask, get_spread, get_balance
import os

class PaperTrader:
    def __init__(self, params):
        '''
        params = {
            'trade_position_usd': float,
            'trade_position_asset': float,
            'asset_pair': str
            }
        '''
        try:
            strategy = '' ## Load from config. Should be a python file.
            strat = strategy()
            self.params = params
            try:
                os.remove('data/strategy-statistics.json')
                os.remove('data/last_trade.json')
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"[ERROR] PaperTrader.__init__() encounted an error: {e}")

        except Exception as e:
            print(f"[ERROR] PaperTrader.__init__() encounted an error: {e}")

    def run_trader(self, time=-1):
        i = 0
        while i <= time:
            try:
                self.strategy.should_buy()
                self.strategy.should_sell()
            except NameError:
                print(f'[ERROR] PaperTrader.run_trader(): Strategy not well defined. Refer to documentation.')
            except Exception as e:
                print(f"[ERROR] PaperTrader.run_trader() encounted an erorr: {e}")
            if time!=-1:
                i+=1

        print('Paper trader finished.')
        print('-'*20)
        print(f"PNL($): ${-1.00}")
        print(f"PNL(%): {-1.00}%")
        print(f"Total Trades: {-1}")
        print(f"Volume: {-1}")
        print('-'*20)

        
