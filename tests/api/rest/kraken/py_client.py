import sys
import os
# sys.path.append('../../../src/clients')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "src", "clients")))

from kraken_python_client import KrakenPythonClient

def main():
    kraken = KrakenPythonClient()
    
    fails = 0 
    cases = 7

    print('='*60)
    print('Testing get_bid')
    try:
        print(kraken.get_bid())
    except Exception as e:
        print(f"!ERROR! {e}")
        fails+=1
    print('='*60)
    print('')
    
    print('='*60)
    print('Testing get_ask')
    try:
        print(kraken.get_ask())
    except Exception as e:
        print(f"!ERROR! {e}")
        fails+=1
    print('='*60)
    print('')

    print('='*60)
    print('Testing get_balance')
    try:
        print(kraken.get_balance())
    except Exception as e:
        print(f"!ERROR! {e}")
        fails+=1
    print('='*60)
    print('')

    print('='*60)
    print('Testing get_balance for USD')
    try:
        print(kraken.get_balance('ZUSD'))
    except Exception as e:
        print(f"!ERROR! {e}")
        fails+=1
    print('='*60)
    print('')

    print('='*60)
    print('Testing get_spread')
    try:
        print(kraken.get_spread())
    except Exception as e:
        print(f"!ERROR! {e}")
        fails+=1
    print('='*60)
    print('')


    print('='*60)
    print('Testing add_order')
    try:
        print('')
        #print(kraken.add_order('XBTUSD','buy',1,1))
    except Exception as e:
        print(f"!ERROR! {e}")
        fails+=1
    print('='*60)
    print('')
    
    print('='*60)
    print('Testing get_open_orders')
    try:
        orders = kraken.get_open_orders(asset='EURQUSD')
        print(orders)
    except Exception as e:
        print(f"!ERROR! {e}")
        fails+=1
    print('='*60)
    print('')
    

    print(' ')
    print('='*60)
    print('Results')
    print(f'Cases Passed: {cases-fails}')
    print(f'Cases Failed: {fails}')
    print('='*60)

    

if __name__ == "__main__":
    main()