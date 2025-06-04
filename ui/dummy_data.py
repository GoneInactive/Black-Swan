import json
import random
from datetime import datetime, timedelta
import os
import time

# Constants (taken from the original program)
CRYPTO_ASSETS = ['BTC', 'ETH', 'SOL', 'LTC', 'XRP', 'ADA']
COMMODITIES = ['Gold', 'Silver', 'Oil', 'NatGas']
INDICES = ['SPX', 'NDX', 'DJI', 'RUT']

# Base prices for different assets
BASE_PRICES = {
    'BTC': 65000.0,
    'ETH': 3500.0,
    'SOL': 125.0,
    'LTC': 80.0,
    'XRP': 0.55,
    'ADA': 0.45,
    'Gold': 2100.0,
    'Silver': 31.0,
    'Oil': 75.0,
    'NatGas': 2.3,
    'SPX': 5150.0,
    'NDX': 18000.0,
    'DJI': 40000.0,
    'RUT': 2000.0
}

def generate_crypto_price_data():
    """Generate dummy price data for each crypto asset."""
    now = datetime.now()
    results = {}
    
    for asset in CRYPTO_ASSETS:
        # Generate 24 hours of data with hourly timestamps
        timestamps = [(now - timedelta(hours=x)).strftime("%Y-%m-%d %H:%M:%S") 
                    for x in range(24, 0, -1)]
        
        # Start with the base price for this asset
        base_price = BASE_PRICES.get(asset, 100.0)
        
        # Generate price series with random walk
        prices = [base_price]
        for i in range(1, 24):
            # Higher volatility for crypto assets (-2% to +2% per hour)
            change_pct = (random.random() - 0.5) * 0.04
            prices.append(round(prices[-1] * (1 + change_pct), 2))
        
        # Create the data structure
        price_data = [{"timestamp": ts, asset: p} for ts, p in zip(timestamps, prices)]
        results[asset] = price_data
    
    return results

def generate_strategy_pnl():
    """Generate dummy strategy PnL data for the past 30 days."""
    now = datetime.now()
    timestamps = [(now - timedelta(days=x)).strftime("%Y-%m-%d") 
                for x in range(30, 0, -1)]
    
    # Start with initial PnL
    pnl = [10000.0]  # Starting account value
    
    # Generate random PnL changes with a slight upward bias
    for i in range(1, 30):
        daily_return = (random.random() - 0.45) * 0.02  # Slight bias towards positive returns
        pnl.append(round(pnl[-1] * (1 + daily_return), 2))
    
    # Create the data structure
    pnl_data = [{"timestamp": ts, "pnl": p} for ts, p in zip(timestamps, pnl)]
    
    return pnl_data

def generate_strategy_stats():
    """Generate dummy strategy stats."""
    return {
        "Strategy Name": "TradeByte Crypto Alpha",
        "Return": f"{random.uniform(10, 25):.2f}%",
        "Sharpe": f"{random.uniform(1.5, 2.5):.2f}",
        "Drawdown": f"-{random.uniform(5, 12):.2f}%",
        "Win Rate": f"{random.uniform(55, 70):.1f}%",
        "Status": "ACTIVE"
    }

def generate_crypto_market_data():
    """Generate dummy crypto market data."""
    data = []
    
    for asset in CRYPTO_ASSETS:
        base_price = BASE_PRICES.get(asset, 100.0)
        price = round(base_price * (1 + (random.random() - 0.5) * 0.05), 2)
        
        change = round(price - base_price, 2)
        pct_change = round((change / base_price) * 100, 2)
        
        # Generate volume in thousands or millions
        volume_multiplier = 1000 if asset in ['XRP', 'ADA'] else 100
        volume = round(random.uniform(50, 500) * volume_multiplier)
        
        # Format volume with K or M suffix
        if volume >= 1000:
            volume_str = f"{volume/1000:.1f}M"
        else:
            volume_str = f"{volume}K"
        
        data.append({
            "symbol": asset,
            "price": price,
            "change": change,
            "pct_change": pct_change,
            "volume": volume_str
        })
    
    return data

def generate_commodity_market_data():
    """Generate dummy commodity market data."""
    data = []
    
    for commodity in COMMODITIES:
        base_price = BASE_PRICES.get(commodity, 100.0)
        price = round(base_price * (1 + (random.random() - 0.5) * 0.02), 2)
        
        change = round(price - base_price, 2)
        pct_change = round((change / base_price) * 100, 2)
        
        data.append({
            "symbol": commodity,
            "price": price,
            "change": change,
            "pct_change": pct_change
        })
    
    return data

def generate_indices_market_data():
    """Generate dummy indices market data."""
    data = []
    
    for index in INDICES:
        base_price = BASE_PRICES.get(index, 1000.0)
        price = round(base_price * (1 + (random.random() - 0.5) * 0.015), 2)
        
        change = round(price - base_price, 2)
        pct_change = round((change / base_price) * 100, 2)
        
        data.append({
            "symbol": index,
            "price": price,
            "change": change,
            "pct_change": pct_change
        })
    
    return data

def generate_positions_data():
    """Generate dummy positions data."""
    data = []
    
    # Generate positions for a subset of crypto assets
    position_assets = random.sample(CRYPTO_ASSETS, 3)  # Have positions in 3 random assets
    
    for asset in position_assets:
        base_price = BASE_PRICES.get(asset, 100.0)
        
        # Generate entry price with slight difference from base
        avg_price = round(base_price * (1 - random.uniform(0.01, 0.05)), 2)
        
        # Generate random position size appropriate for the asset
        if asset == 'BTC':
            quantity = round(random.uniform(0.5, 2.0), 3)
        elif asset in ['ETH', 'SOL']:
            quantity = round(random.uniform(5, 15), 2)
        else:
            quantity = round(random.uniform(50, 200), 1)
        
        current_price = BASE_PRICES.get(asset, 100.0) * (1 + (random.random() - 0.4) * 0.03)
        market_value = round(quantity * current_price, 2)
        pnl = round(market_value - (quantity * avg_price), 2)
        
        data.append({
            "symbol": asset,
            "quantity": quantity,
            "avg_price": avg_price,
            "market_value": market_value,
            "pnl": pnl
        })
    
    return data

def generate_news_data():
    """Generate dummy news data."""
    news_headlines = [
        {"time": "10:23 AM", "headline": "Bitcoin Surges Past $65K on Institutional Buying", "source": "CryptoNews"},
        {"time": "09:45 AM", "headline": "SEC Approves New Ethereum ETF Applications", "source": "Bloomberg"},
        {"time": "09:12 AM", "headline": "Solana DeFi TVL Reaches All-Time High", "source": "DeFi Pulse"},
        {"time": "08:55 AM", "headline": "Fed Signals Continued Caution on Rate Cuts", "source": "Reuters"},
        {"time": "08:30 AM", "headline": "Asian Markets Close Mixed Amid Tech Rally", "source": "CNBC"},
        {"time": "08:15 AM", "headline": "New Regulatory Framework for Crypto Proposed in EU", "source": "CoinDesk"},
        {"time": "07:55 AM", "headline": "Oil Prices Fall on Inventory Build", "source": "Market Watch"},
        {"time": "07:30 AM", "headline": "Gold Hits Record High on Inflation Concerns", "source": "Financial Times"},
        {"time": "07:15 AM", "headline": "Major Bank Announces Crypto Custody Service", "source": "Banking Daily"},
        {"time": "07:00 AM", "headline": "Tech Stocks Lead Market Rally", "source": "Wall Street Journal"}
    ]
    
    return news_headlines

def main():
    """Generate all dummy data and save to JSON files in the exact format expected by the original program."""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created data directory")
    
    # 1. Generate crypto price data for each asset
    # File format: data/{asset.lower()}_prices.json
    crypto_prices = generate_crypto_price_data()
    for asset, data in crypto_prices.items():
        filename = f'data/{asset.lower()}_prices.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated price data for {asset} -> {filename}")
    
    # 2. Generate strategy PnL
    # File format: data/strategy_pnl.json
    pnl_data = generate_strategy_pnl()
    with open('data/strategy_pnl.json', 'w') as f:
        json.dump(pnl_data, f, indent=2)
    print("Generated strategy PnL data -> data/strategy_pnl.json")
    
    # 3. Generate strategy stats
    # File format: data/strategy_stats.json
    stats_data = generate_strategy_stats()
    with open('data/strategy_stats.json', 'w') as f:
        json.dump(stats_data, f, indent=2)
    print("Generated strategy stats data -> data/strategy_stats.json")
    
    # 4. Generate market data
    # File format: data/crypto_market.json
    crypto_market_data = generate_crypto_market_data()
    with open('data/crypto_market.json', 'w') as f:
        json.dump(crypto_market_data, f, indent=2)
    print("Generated crypto market data -> data/crypto_market.json")
    
    # File format: data/commodities_market.json
    commodities_data = generate_commodity_market_data()
    with open('data/commodities_market.json', 'w') as f:
        json.dump(commodities_data, f, indent=2)
    print("Generated commodities market data -> data/commodities_market.json")
    
    # File format: data/indices_market.json
    indices_data = generate_indices_market_data()
    with open('data/indices_market.json', 'w') as f:
        json.dump(indices_data, f, indent=2)
    print("Generated indices market data -> data/indices_market.json")
    
    # 5. Generate positions data
    # File format: data/positions.json
    positions_data = generate_positions_data()
    with open('data/positions.json', 'w') as f:
        json.dump(positions_data, f, indent=2)
    print("Generated positions data -> data/positions.json")
    
    # 6. Generate news data
    # File format: data/news.json
    news_data = generate_news_data()
    with open('data/news.json', 'w') as f:
        json.dump(news_data, f, indent=2)
    print("Generated news data -> data/news.json")
    
    print("\nAll dummy data has been generated successfully!")
    print("The TradeByte Terminal should now work with this data.")
    print("Run your original application to see the generated data in action.")

if __name__ == "__main__":
    for _ in range(100):
        main()
        time.sleep(6)