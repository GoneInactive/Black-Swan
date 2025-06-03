import time
from rust_ws_py import subscribe, get_orderbook, add_order, get_orders, close_orders, test_connection

def main():
    print("Testing connection...")
    try:
        test_connection()
        print("Connection test succeeded.")
    except Exception as e:
        print(f"Connection test failed: {e}")
    print("Subscribing to ticker feed...")
    subscribe("XBT/USD")

    time.sleep(1)  # slight delay between calls

    print("Requesting order book...")
    get_orderbook("XBT/USD", 10)  # add depth parameter

    time.sleep(1)

    print("Testing order functions...")

    # Market buy 0.01 XBT/USD
    add_order("XBT/USD", "buy", 0.01, "market")

    time.sleep(1)

    # Fetch open orders
    get_orders()

    time.sleep(1)

    # Cancel orders by txid (replace with actual txids)
    close_orders(["OID123456", "OID654321"])

    print("Listening for WebSocket messages...")
    time.sleep(10)
    print("Done.")

if __name__ == "__main__":
    main()