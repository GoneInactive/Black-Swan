import sys
import os
try:
    import rust_kraken_client
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../rust_client/target/debug')))  # or target/release if built in release mode
    import rust_kraken_client
import json

def test_kraken():
    """Test all Kraken API functions"""
    results = {}
    
    # Test public API endpoints
    try:
        print("Testing Kraken public API endpoints...")
        results['bid'] = rust_kraken_client.get_bid()
        print(f"✓ Bid: {results['bid']}")
    except Exception as e:
        results['bid_error'] = str(e)
        print(f"✗ Bid error: {e}")
    
    try:
        results['ask'] = rust_kraken_client.get_ask()
        print(f"✓ Ask: {results['ask']}")
    except Exception as e:
        results['ask_error'] = str(e)
        print(f"✗ Ask error: {e}")
    
    try:
        results['spread'] = rust_kraken_client.get_spread()
        print(f"✓ Spread: {results['spread']}")
    except Exception as e:
        results['spread_error'] = str(e)
        print(f"✗ Spread error: {e}")
    
    # Test private API endpoints (balance functions)
    print("\nTesting Kraken private API endpoints...")
    try:
        results['balance'] = rust_kraken_client.get_balance()
        print(f"✓ USD Balance: {results['balance']}")
    except Exception as e:
        results['balance_error'] = str(e)
        print(f"✗ Balance error: {e}")
    
    # Test balance for specific asset (Bitcoin)
    try:
        results['btc_balance'] = rust_kraken_client.get_balance_for_asset("XXBT")
        print(f"✓ BTC Balance: {results['btc_balance']}")
    except Exception as e:
        results['btc_balance_error'] = str(e)
        print(f"✗ BTC Balance error: {e}")
    
    # Test balance for Ethereum
    try:
        results['eth_balance'] = rust_kraken_client.get_balance_for_asset("XETH")
        print(f"✓ ETH Balance: {results['eth_balance']}")
    except Exception as e:
        results['eth_balance_error'] = str(e)
        print(f"✗ ETH Balance error: {e}")
    
    # Test getting all balances
    try:
        all_balances = rust_kraken_client.get_all_balances()
        results['all_balances'] = all_balances
        results['total_assets'] = len(all_balances)
        print(f"✓ Total assets with balance: {results['total_assets']}")
        
        # Show non-zero balances
        non_zero_balances = {k: v for k, v in all_balances.items() if v > 0}
        if non_zero_balances:
            print("Non-zero balances:")
            for asset, balance in non_zero_balances.items():
                print(f"  {asset}: {balance}")
        else:
            print("No non-zero balances found")
            
    except Exception as e:
        results['all_balances_error'] = str(e)
        print(f"✗ All balances error: {e}")
    
    # Calculate success rate
    error_keys = [k for k in results.keys() if k.endswith('_error')]
    total_tests = len([k for k in results.keys() if not k.endswith('_error')])
    success_rate = ((total_tests - len(error_keys)) / max(total_tests, 1)) * 100
    results['success_rate'] = success_rate
    
    return results

def test_market_data_analysis():
    """Perform additional market data analysis"""
    print("\n" + "="*50)
    print("MARKET DATA ANALYSIS")
    print("="*50)
    
    try:
        bid = rust_kraken_client.get_bid()
        ask = rust_kraken_client.get_ask()
        spread = rust_kraken_client.get_spread()
        
        # Calculate spread percentage
        mid_price = (bid + ask) / 2
        spread_percentage = (spread / mid_price) * 100
        
        print(f"Bid Price: ${bid:,.2f}")
        print(f"Ask Price: ${ask:,.2f}")
        print(f"Mid Price: ${mid_price:,.2f}")
        print(f"Spread: ${spread:,.2f}")
        print(f"Spread %: {spread_percentage:.4f}%")
        
        # Market assessment
        if spread_percentage < 0.01:
            market_condition = "Very tight spread - high liquidity"
        elif spread_percentage < 0.05:
            market_condition = "Normal spread - good liquidity"
        elif spread_percentage < 0.1:
            market_condition = "Wide spread - moderate liquidity"
        else:
            market_condition = "Very wide spread - low liquidity"
            
        print(f"Market Condition: {market_condition}")
        
        return {
            'bid': bid,
            'ask': ask,
            'mid_price': mid_price,
            'spread': spread,
            'spread_percentage': spread_percentage,
            'market_condition': market_condition
        }
        
    except Exception as e:
        print(f"Market analysis error: {e}")
        return {'error': str(e)}

def test_balance_analysis():
    """Perform balance analysis if authentication works"""
    print("\n" + "="*50)
    print("BALANCE ANALYSIS")
    print("="*50)
    
    try:
        all_balances = rust_kraken_client.get_all_balances()
        
        if not all_balances:
            print("No balances found or authentication failed")
            return {'error': 'No balances available'}
        
        # Filter non-zero balances
        active_balances = {k: v for k, v in all_balances.items() if v > 0}
        
        if not active_balances:
            print("All balances are zero")
            return {'total_assets': 0, 'active_assets': 0}
        
        print(f"Total assets tracked: {len(all_balances)}")
        print(f"Assets with balance: {len(active_balances)}")
        print("\nActive Balances:")
        
        for asset, balance in sorted(active_balances.items()):
            print(f"  {asset}: {balance:,.8f}")
        
        return {
            'total_assets': len(all_balances),
            'active_assets': len(active_balances),
            'balances': active_balances
        }
        
    except Exception as e:
        print(f"Balance analysis error: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    print("="*60)
    print("KRAKEN API COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Test all Kraken API functions
    kraken_results = test_kraken()
    
    # Perform market data analysis
    market_analysis = test_market_data_analysis()
    
    # Perform balance analysis
    balance_analysis = test_balance_analysis()
    
    # Summary report
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)
    
    print(f"API Test Success Rate: {kraken_results.get('success_rate', 0):.1f}%")
    
    if 'error' not in market_analysis:
        print(f"Market Spread: {market_analysis.get('spread_percentage', 0):.4f}%")
    
    if 'error' not in balance_analysis:
        print(f"Active Assets: {balance_analysis.get('active_assets', 0)}")
    
    # Detailed results
    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    
    print("\nKraken API Test Results:")
    for key, value in kraken_results.items():
        if not key.endswith('_error') and key != 'all_balances':
            print(f"  {key}: {value}")
    
    # Show errors if any
    error_keys = [k for k in kraken_results.keys() if k.endswith('_error')]
    if error_keys:
        print("\nErrors encountered:")
        for key in error_keys:
            print(f"  {key}: {kraken_results[key]}")
    
    print("\nTest completed!")