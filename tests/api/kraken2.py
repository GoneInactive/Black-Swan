#!/usr/bin/env python3
"""
Test script for rust_kraken_client Python extension module.
Tests all exposed functions from the Rust library.
"""

import sys
import json
from typing import Dict, Any
import os
try:
    import rust_kraken_client
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../rust_client/target/debug')))  # or target/release if built in release mode
    import rust_kraken_client
import json

def test_kraken_functions():
    """Test all Kraken API functions."""
    print("=" * 60)
    print("TESTING KRAKEN API FUNCTIONS")
    print("=" * 60)
    
    # Test get_bid()
    print("\n1. Testing get_bid()...")
    try:
        bid = rust_kraken_client.get_bid()
        print(f"✓ Bid price: ${bid:.2f}")
    except Exception as e:
        print(f"✗ Error getting bid: {e}")
    
    # Test get_ask()
    print("\n2. Testing get_ask()...")
    try:
        ask = rust_kraken_client.get_ask()
        print(f"✓ Ask price: ${ask:.2f}")
    except Exception as e:
        print(f"✗ Error getting ask: {e}")
    
    # Test get_spread()
    print("\n3. Testing get_spread()...")
    try:
        spread = rust_kraken_client.get_spread()
        print(f"✓ Spread: ${spread:.4f}")
        
        # Calculate spread percentage if we have both bid and ask
        try:
            bid = rust_kraken_client.get_bid()
            spread_percent = (spread / bid) * 100
            print(f"✓ Spread percentage: {spread_percent:.4f}%")
        except:
            pass
    except Exception as e:
        print(f"✗ Error getting spread: {e}")
    
    # Test get_balance() - this requires API credentials
    print("\n4. Testing get_balance()...")
    try:
        balances = rust_kraken_client.get_balance()
        print("✓ Account balances:")
        
        if isinstance(balances, dict):
            # Filter out zero balances for cleaner output
            non_zero_balances = {k: v for k, v in balances.items() if v > 0}
            
            if non_zero_balances:
                for currency, balance in non_zero_balances.items():
                    print(f"  {currency}: {balance:.8f}")
            else:
                print("  No non-zero balances found")
                print(f"  Total currencies in account: {len(balances)}")
        else:
            print(f"  Unexpected balance format: {type(balances)}")
            
    except Exception as e:
        print(f"✗ Error getting balance: {e}")
        print("  Note: This requires valid API credentials in config/config.yaml")

def test_order_functions():
    """Test order-related functions (requires API credentials)."""
    print("\n" + "=" * 60)
    print("TESTING ORDER FUNCTIONS")
    print("=" * 60)
    
    try:
        import rust_kraken_client
    except ImportError as e:
        print(f"✗ Module not available: {e}")
        return False
    
    # Test add_order() - DEMO MODE (will fail without real credentials)
    print("\n1. Testing add_order() - DEMO MODE...")
    print("⚠️  This is a demonstration of the add_order function.")
    print("⚠️  It will fail without valid API credentials and sufficient balance.")
    
    try:
        # Example order parameters (small amount for safety)
        pair = "XBTUSD"  # Bitcoin/USD
        side = "buy"     # Buy order
        price = 1.0      # Very low price (order won't execute)
        volume = 0.001   # Small volume
        
        print(f"  Attempting to place order:")
        print(f"    Pair: {pair}")
        print(f"    Side: {side}")
        print(f"    Price: ${price}")
        print(f"    Volume: {volume}")
        
        order_response = rust_kraken_client.add_order(pair, side, price, volume)
        
        print("✓ Order placed successfully!")
        print(f"  Transaction IDs: {order_response.txid}")
        print(f"  Description: {order_response.description}")
        
    except Exception as e:
        print(f"✗ Error placing order: {e}")
        print("  Expected - this requires:")
        print("    - Valid API credentials with trading permissions")
        print("    - Sufficient account balance")
        print("    - Proper pair format")
    
    # Test parameter validation
    print("\n2. Testing add_order() parameter validation...")
    try:
        # Test invalid side parameter
        rust_kraken_client.add_order("XBTUSD", "invalid_side", 50000.0, 0.001)
    except Exception as e:
        if "Side must be 'buy' or 'sell'" in str(e):
            print("✓ Parameter validation working - invalid side rejected")
        else:
            print(f"✗ Unexpected error: {e}")
    
    print("\n📝 Order Function Notes:")
    print("- add_order(pair, side, price, volume)")
    print("- pair: Trading pair (e.g., 'XBTUSD', 'ETHUSD')")
    print("- side: 'buy' or 'sell'")
    print("- price: Limit price as float")
    print("- volume: Order size as float")
    print("- Returns: OrderResponse with txid and description")
    print("- Requires: API credentials with trading permissions")

def test_binance_functions():
    """Test all Binance API functions."""
    print("\n" + "=" * 60)
    print("TESTING BINANCE API FUNCTIONS")
    print("=" * 60)
    
    try:
        import rust_kraken_client
    except ImportError as e:
        print(f"✗ Module not available: {e}")
        return False
    
    # Test get_binance_depth()
    print("\n1. Testing get_binance_depth()...")
    try:
        depth_json = rust_kraken_client.get_binance_depth()
        print("✓ Successfully retrieved Binance order book depth")
        
        # Parse and display some info about the depth data
        try:
            depth_data = json.loads(depth_json)
            
            if isinstance(depth_data, dict):
                print(f"✓ Order book data structure:")
                for key in depth_data.keys():
                    if key == 'bids' and isinstance(depth_data[key], list):
                        print(f"  {key}: {len(depth_data[key])} entries")
                        if depth_data[key]:
                            best_bid = depth_data[key][0]
                            print(f"    Best bid: {best_bid}")
                    elif key == 'asks' and isinstance(depth_data[key], list):
                        print(f"  {key}: {len(depth_data[key])} entries")
                        if depth_data[key]:
                            best_ask = depth_data[key][0]
                            print(f"    Best ask: {best_ask}")
                    else:
                        print(f"  {key}: {depth_data[key]}")
            else:
                print(f"  Raw data: {depth_json[:200]}...")
                
        except json.JSONDecodeError as e:
            print(f"  Raw response (first 200 chars): {depth_json[:200]}...")
            
    except Exception as e:
        print(f"✗ Error getting Binance depth: {e}")

def test_combined_analysis():
    """Perform some combined analysis using multiple functions."""
    print("\n" + "=" * 60)
    print("COMBINED ANALYSIS")
    print("=" * 60)
    
    try:
        import rust_kraken_client
        
        print("\nTrying to compare Kraken and Binance data...")
        
        # Get Kraken data
        kraken_bid = None
        kraken_ask = None
        
        try:
            kraken_bid = rust_kraken_client.get_bid()
            kraken_ask = rust_kraken_client.get_ask()
            print(f"✓ Kraken - Bid: ${kraken_bid:.2f}, Ask: ${kraken_ask:.2f}")
        except Exception as e:
            print(f"✗ Failed to get Kraken prices: {e}")
        
        # Get Binance data
        try:
            binance_depth_json = rust_kraken_client.get_binance_depth()
            binance_depth = json.loads(binance_depth_json)
            
            if 'bids' in binance_depth and 'asks' in binance_depth:
                if binance_depth['bids'] and binance_depth['asks']:
                    binance_bid = float(binance_depth['bids'][0][0])
                    binance_ask = float(binance_depth['asks'][0][0])
                    print(f"✓ Binance - Bid: ${binance_bid:.2f}, Ask: ${binance_ask:.2f}")
                    
                    # Compare if we have both
                    if kraken_bid and kraken_ask:
                        bid_diff = abs(kraken_bid - binance_bid)
                        ask_diff = abs(kraken_ask - binance_ask)
                        print(f"\n📊 Price Comparison:")
                        print(f"  Bid difference: ${bid_diff:.2f}")
                        print(f"  Ask difference: ${ask_diff:.2f}")
                        
                        if bid_diff > 100 or ask_diff > 100:
                            print("  ⚠️  Large price difference detected - might be different trading pairs")
                        
        except Exception as e:
            print(f"✗ Failed to get Binance data: {e}")
            
    except Exception as e:
        print(f"✗ Error in combined analysis: {e}")

def run_all_tests():
    """Run all test functions."""
    print("🚀 Starting rust_kraken_client test suite...")
    print(f"Python version: {sys.version}")
    
    # Test Kraken functions
    test_kraken_functions()
    
    # Test order functions
    test_order_functions()
    
    # Test Binance functions  
    test_binance_functions()
    
    # Combined analysis
    test_combined_analysis()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    
    print("\n📝 Notes:")
    print("- Public API calls (bid, ask, spread, binance_depth) should work without credentials")
    print("- Private API calls (balance) require valid API keys in config/config.yaml")
    print("- Make sure your config file has the correct structure:")
    print("  kraken:")
    print("    api_key: 'your-api-key'")
    print("    api_secret: 'your-api-secret'") 
    print("    default_pair: 'XBTUSD'  # or your preferred pair")

if __name__ == "__main__":
    run_all_tests()