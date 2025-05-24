import sys
import os

from src.handler.components.start_strategy import StartStrategy

class CommandHandler:
    def __init__(self):
        pass

    def start(self, strategy: str, exchange: str, *args, **kwargs):
        """
        METHOD: Start (Strategy) (Exchange) (Args)
        Example: Start sma binance 1h 0.001 0.01
        """
        start_strategy = StartStrategy(strategy, exchange, *args, **kwargs)
        start_strategy.start()

    def command(self, command: str, *args, **kwargs):
        cmd = command.split() # Splits the command into a list of arguments based on spaces

        ## TODO: Start Trading a Strategy
        if "start" in cmd:
            self.start(cmd[1], cmd[2], *cmd[3:])    
        elif cmd == "q":
            sys.exit()
        elif cmd == "help":
            ## TODO: Show help
            pass
        else:
            print('Invalid command')
            return False

