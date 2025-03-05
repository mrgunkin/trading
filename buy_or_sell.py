import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Функция для получения текущей цены с Binance API
def get_binance_data(symbol="BTCUSDT", interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                         'close_time', 'quote_asset_volume', 'trades', 
                                         'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[['timestamp', 'close', 'volume']]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Параметры из Pine Script
lookback = 13
showMA = True
lengthMA = 55
tickername = "BINANCE:BTCUSDT"  # Используем BTCUSDT на Binance
interval = "1h"  # Используем интервал 1 час для начала

# Функция для определения порогового объема (b1) в зависимости от таймфрейма
def get_volume_threshold(tickername, timeframe):
    if tickername == "BINANCE:BTCUSDT":
        if timeframe == "1":
            return 150
        elif timeframe == "5":
            return 1000
        elif timeframe == "15":
            return 1500
        elif timeframe == "30":
            return 3000
        elif timeframe == "60":
            return 6000
        elif timeframe == "120":
            return 11000
        elif timeframe == "240":
            return 15000
        elif timeframe == "D":
            return 50000
    return None

# Функция для расчета цвета баров
def calculate_bar_color(current_close, prev_close, current_volume, prev_volume):
    if current_close < prev_close and current_volume > prev_volume:
        return '#4CAF50'  # Зеленый (покупка)
    elif current_close < prev_close and current_volume < prev_volume:
        return '#B2B5BE'  # Серый
    elif current_close > prev_close and current_volume < prev_volume:
        return '#B2B5BE'  # Серый
    elif current_close > prev_close and current_volume > prev_volume:
        return '#FF5252'  # Красный (продажа)
    return '#B2B5BE'  # По умолчанию серый

# Функция для обновления графиков
def update_plot(frame, ax_price, ax_volume, df):
    ax_price.cla()  # Очистка графика цены
    ax_volume.cla()  # Очистка графика объема
    
    # Вычисляем данные для графиков
    prices = df['close'].values
    volumes = df['volume'].values
    timestamps = df['timestamp'].values
    
    # Расчет скользящей средней объема
    ma_volume = pd.Series(volumes).rolling(window=lengthMA, center=False).mean()
    
    # Пороговый уровень объема для текущего интервала
    volume_threshold = get_volume_threshold(tickername, interval.replace("m", "").replace("h", ""))
    
    # Цвета для баров
    bar_colors = [calculate_bar_color(prices[i], prices[i-lookback] if i >= lookback else prices[0], 
                                    volumes[i], volumes[i-lookback] if i >= lookback else volumes[0]) 
                  for i in range(len(prices))]
    
    # График цены (сверху)
    ax_price.plot(timestamps, prices, 'b-', label='BTC Price')
    ax_price.set_title('Bitcoin Price and BuySell Volume')
    ax_price.set_xlabel('Time')
    ax_price.set_ylabel('Price (USDT)')
    ax_price.legend()
    ax_price.grid(True)
    ax_price.tick_params(axis='x', rotation=45)
    
    # График объема (снизу)
    ax_volume.bar(timestamps, volumes, color=bar_colors, width=0.002, label='Volume')
    
    # Отрисовка скользящей средней (если включена)
    if showMA and len(ma_volume) == len(timestamps):
        ax_volume.plot(timestamps, ma_volume, 'orange', alpha=0.6, label='Volume MA', linewidth=2)
    
    # Отрисовка порогового уровня
    if volume_threshold:
        ax_volume.axhline(y=volume_threshold, color='orange', linestyle='--', alpha=0.4, linewidth=3, label='Volume Threshold')
    
    ax_volume.set_xlabel('Time')
    ax_volume.set_ylabel('Volume')
    ax_volume.legend()
    ax_volume.grid(True)
    
    # Автоматическое масштабирование
    ax_price.relim()
    ax_price.autoscale_view()
    ax_volume.relim()
    ax_volume.autoscale_view()

def main():
    # Получаем данные
    df = get_binance_data(symbol="BTCUSDT", interval=interval, limit=100)
    if df is None or len(df) < lookback:
        print("Not enough data to plot. Exiting.")
        return
    
    # Настройка графиков (два подграфика)
    fig, (ax_price, ax_volume) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ani = FuncAnimation(fig, update_plot, fargs=(ax_price, ax_volume, df), interval=5000)  # Обновление каждые 5 секунд
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Убедитесь, что установлены все зависимости:
    # pip install pandas requests matplotlib numpy
    main()