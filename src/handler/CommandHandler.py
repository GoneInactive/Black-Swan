import sys
import os

from handler.components.start_strategy import StartStrategy

import subprocess
import sys
import os

class CommandHandler:
    def __init__(self):
        pass

    def start(self, strategy: str, exchange: str, *args, **kwargs):
        """
        METHOD: Start (Strategy) (Exchange) (Args)
        Example: Start sma binance 1h 0.001 0.01
        """
        script_path = os.path.join('src', 'apps', 'strategies', f'{strategy}.py')
    
        if not os.path.isfile(script_path):
            print(f"Strategy script not found: {script_path}")
            #print(f"Current Path: {os.getcwd()}")
            return

        cmd = [sys.executable, script_path, exchange] + list(args)
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Strategy execution failed: {e}")

    def restart(self):
        print("Restarting TradeByte...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def handle(self, command: str, *args, **kwargs):
        cmd = command.split() # Splits the command into a list of arguments based on spaces

        ## TODO: Start Trading a Strategy
        if "start" in cmd:
            try:
                if len(cmd) == 2:
                    self.start(cmd[1], "default", *cmd[2:])
                else:
                    self.start(cmd[1], cmd[2], *cmd[3:])
            except IndexError:
                print('Error handling arguments.')
                print('Example: start sma kraken')
                print('OR')
                print('Example: start sma')
                print('OR')
                print('Example: start sma kraken 5 day 2')
                print('OR')
                print('Example: start sma 5 day 2')
                print('')
            except Exception as e:
                print(f'!!!COMMAND ERROR!!! {e}')
        elif "exit" in cmd or "quit" in cmd:
            sys.exit()
        elif "help" in cmd:
            try:
                with open('src/handler/docs/help.txt', 'r') as f:
                    help_text = f.readlines()
                
                print('')
                for line in help_text:
                    print(line.strip())

            except FileNotFoundError:
                print('Error. help.txt is missing.')
            except Exception as e:
                print(f'!!!COMMAND ERROR!!! {e}')
        elif "path" in cmd:
            print(sys.path)

        elif "restart" in cmd:
            self.restart()
        else:
            print('Invalid command')
            
