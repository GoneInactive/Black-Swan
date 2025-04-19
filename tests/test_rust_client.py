from rust_kraken_client import get_bid, get_ask, get_spread, get_balance

def test_rust_client():
    print("Testing Kraken Client:")
    try:
        bid = get_bid()
        print(f"Bid: {bid}")
    except Exception as e:
        print(f"Error getting bid: {e}")
    
    try:
        ask = get_ask()
        print(f"Ask: {ask}")
    except Exception as e:
        print(f"Error getting ask: {e}")

    try:
        spread = get_spread()
        print(f"Spread (Ask - Bid): {spread}")
    except Exception as e:
        print(f"Error getting spread: {e}")
    
    try:
        balance = get_balance()
        print(f"Balance: {balance}")
    except Exception as e:
        print(f"Error getting balance: {e}")

if __name__ == "__main__":
    test_rust_client()
