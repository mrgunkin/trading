import pandas as pd
import requests
import time
from datetime import datetime, timedelta

# Function to get price data from Binance API
def get_price_data(symbol="BTCUSDT", timeframe="1h", limit=13):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                         'close_time', 'quote_asset_volume', 'trades', 
                                         'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[['timestamp', 'close']]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to calculate liquidation levels
def calculate_liquidation_levels(price, level_10=0.10, level_25=0.25):
    upper_10 = price * (1 + level_10)  # +10% level
    lower_10 = price * (1 - level_10)  # -10% level
    upper_25 = price * (1 + level_25)  # +25% level
    lower_25 = price * (1 - level_25)  # -25% level
    return upper_10, lower_10, upper_25, lower_25

# Main trading bot logic for Bitcoin
def bitcoin_trading_bot(check_interval=300):  # Check interval in seconds (default: 5 minutes)
    print("Starting Bitcoin (BTC/USDT) trading bot...")
    print(f"Price check interval: {check_interval} seconds")
    
    while True:
        try:
            # Get price data for the last 13 hours (12 + current)
            df = get_price_data()
            if df is None or len(df) < 13:
                print("Not enough data for analysis. Skipping this cycle.")
                time.sleep(check_interval)
                continue
            
            # Price 12 hours ago and current price
            price_12h_ago = df['close'].iloc[0]
            current_price = df['close'].iloc[-1]
            current_time = df['timestamp'].iloc[-1]
            
            # Calculate liquidation levels based on price 12 hours ago
            upper_10, lower_10, upper_25, lower_25 = calculate_liquidation_levels(price_12h_ago)
            
            # Display current price and levels
            print(f"[{current_time}] Current Bitcoin price: ${current_price:.2f}")
            print(f"Levels from 12 hours ago (${price_12h_ago:.2f}): "
                  f"+10%: ${upper_10:.2f}, -10%: ${lower_10:.2f}, "
                  f"+25%: ${upper_25:.2f}, -25%: ${lower_25:.2f}")
            
            # Check proximity to liquidation levels (within 1%)
            if abs(current_price - upper_10) / upper_10 < 0.01:
                print("⚠️ Warning: Price nearing +10% level! Recommendation: Consider shorting.")
            elif abs(current_price - lower_10) / lower_10 < 0.01:
                print("⚠️ Warning: Price nearing -10% level! Recommendation: Consider longing.")
            elif abs(current_price - upper_25) / upper_25 < 0.01:
                print("⚠️ Warning: Price nearing +25% level! Recommendation: Short to lock in profits.")
            elif abs(current_price - lower_25) / lower_25 < 0.01:
                print("⚠️ Warning: Price nearing -25% level! Recommendation: Long on the dip.")
            else:
                print("Price is in a safe zone. Waiting for movement.")
            
            # Wait for the next check
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(check_interval)  # Pause on error

# Start the bot
if __name__ == "__main__":
    # Set check interval (e.g., 300 seconds = 5 minutes)
    bitcoin_trading_bot(check_interval=300)
