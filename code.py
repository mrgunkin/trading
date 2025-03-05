import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import logging
from colorama import init, Fore, Style  # Для цветного вывода в консоли

# Инициализация цветного вывода
init()

# Настройка логирования
logging.basicConfig(
    filename='bitcoin_trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Function to get current price from Binance API
def get_current_price(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current price: {e}")
        return None

# Function to get historical price data from Binance API
def get_historical_price_data(symbol="BTCUSDT", timeframe="1h", limit=13):
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
        print(f"Error fetching historical data: {e}")
        return None

# Function to calculate liquidation levels
def calculate_liquidation_levels(price, level_10=0.10, level_25=0.25):
    upper_10 = price * (1 + level_10)
    lower_10 = price * (1 - level_10)
    upper_25 = price * (1 + level_25)
    lower_25 = price * (1 - level_25)
    return upper_10, lower_10, upper_25, lower_25

# Main trading bot logic
def bitcoin_trading_bot(check_interval=300, proximity_threshold=0.01):
    print("Starting Bitcoin (BTC/USDT) trading bot...")
    print(f"Price check interval: {check_interval} seconds")
    print(f"Proximity threshold: {proximity_threshold*100:.1f}%")
    
    while True:
        try:
            # Get current price
            current_price = get_current_price()
            if current_price is None:
                time.sleep(check_interval)
                continue
            
            # Get historical data for levels
            df = get_historical_price_data()
            if df is None or len(df) < 13:
                print("Not enough historical data. Skipping this cycle.")
                time.sleep(check_interval)
                continue
            
            price_12h_ago = df['close'].iloc[0]
            current_time = datetime.now()
            
            # Calculate liquidation levels
            upper_10, lower_10, upper_25, lower_25 = calculate_liquidation_levels(price_12h_ago)
            
            # Display info
            print(f"[{current_time}] Current Bitcoin price: ${current_price:.2f}")
            print(f"Levels from 12 hours ago (${price_12h_ago:.2f}): "
                  f"+10%: ${upper_10:.2f}, -10%: ${lower_10:.2f}, "
                  f"+25%: ${upper_25:.2f}, -25%: ${lower_25:.2f}")
            
            # Check proximity to levels
            if abs(current_price - upper_10) / upper_10 < proximity_threshold:
                message = "⚠️ Warning: Price nearing +10% level! Recommendation: Consider shorting."
                print(Fore.RED + message + Style.RESET_ALL)
                logging.info(message)
            elif abs(current_price - lower_10) / lower_10 < proximity_threshold:
                message = "⚠️ Warning: Price nearing -10% level! Recommendation: Consider longing."
                print(Fore.GREEN + message + Style.RESET_ALL)
                logging.info(message)
            elif abs(current_price - upper_25) / upper_25 < proximity_threshold:
                message = "⚠️ Warning: Price nearing +25% level! Recommendation: Short to lock in profits."
                print(Fore.RED + message + Style.RESET_ALL)
                logging.info(message)
            elif abs(current_price - lower_25) / lower_25 < proximity_threshold:
                message = "⚠️ Warning: Price nearing -25% level! Recommendation: Long on the dip."
                print(Fore.GREEN + message + Style.RESET_ALL)
                logging.info(message)
            else:
                print("Price is in a safe zone. Waiting for movement.")
            
            # Wait for the next check
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(check_interval)

# Start the bot
if __name__ == "__main__":
    # Install colorama if not already installed: pip install colorama
    bitcoin_trading_bot(check_interval=300, proximity_threshold=0.015)  # 1.5% threshold