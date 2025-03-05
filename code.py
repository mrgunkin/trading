import pandas as pd
import requests
import time
from datetime import datetime, timedelta

# Функция для получения данных о цене с Binance API
def get_price_data(symbol="BTCUSDT", timeframe="1h", limit=13):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                         'close_time', 'quote_asset_volume', 'trades', 
                                         'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[['timestamp', 'close']]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        return None

# Функция для расчета уровней ликвидации
def calculate_liquidation_levels(price, level_10=0.10, level_25=0.25):
    upper_10 = price * (1 + level_10)  # Уровень +10%
    lower_10 = price * (1 - level_10)  # Уровень -10%
    upper_25 = price * (1 + level_25)  # Уровень +25%
    lower_25 = price * (1 - level_25)  # Уровень -25%
    return upper_10, lower_10, upper_25, lower_25

# Основная логика бота для Bitcoin
def bitcoin_trading_bot():
    print("Запуск торгового бота для Bitcoin (BTC/USDT)...")
    
    while True:
        try:
            # Получаем данные за последние 13 часов (12 + текущий час)
            df = get_price_data()
            if df is None or len(df) < 13:
                print("Недостаточно данных для анализа. Пропускаем цикл.")
                time.sleep(60)
                continue
            
            # Цена 12 часов назад (первый элемент) и текущая цена (последний элемент)
            price_12h_ago = df['close'].iloc[0]
            current_price = df['close'].iloc[-1]
            current_time = df['timestamp'].iloc[-1]
            
            # Рассчитываем уровни ликвидации на основе цены 12 часов назад
            upper_10, lower_10, upper_25, lower_25 = calculate_liquidation_levels(price_12h_ago)
            
            # Вывод текущей информации
            print(f"[{current_time}] Текущая цена BTC/USDT: {current_price:.2f}")
            print(f"Уровни 12 часов назад ({price_12h_ago:.2f}): +10%: {upper_10:.2f}, -10%: {lower_10:.2f}, +25%: {upper_25:.2f}, -25%: {lower_25:.2f}")
            
            # Проверка приближения к уровням (в пределах 1% от уровня)
            if abs(current_price - upper_10) / upper_10 < 0.01:
                print("⚠️ Цена приближается к уровню +10%! Рекомендация: Рассмотрите шорт (продажа).")
            elif abs(current_price - lower_10) / lower_10 < 0.01:
                print("⚠️ Цена приближается к уровню -10%! Рекомендация: Рассмотрите лонг (покупка).")
            elif abs(current_price - upper_25) / upper_25 < 0.01:
                print("⚠️ Цена приближается к уровню +25%! Рекомендация: Шорт для фиксации прибыли.")
            elif abs(current_price - lower_25) / lower_25 < 0.01:
                print("⚠️ Цена приближается к уровню -25%! Рекомендация: Лонг на просадке.")
            else:
                print("Цена в безопасной зоне. Ожидаем движения.")
            
            # Пауза 5 минут (300 секунд)
            time.sleep(300)
            
        except Exception as e:
            print(f"Ошибка в работе бота: {e}")
            time.sleep(60)  # Пауза при ошибке

# Запуск бота
if __name__ == "__main__":
    bitcoin_trading_bot()
