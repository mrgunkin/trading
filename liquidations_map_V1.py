import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Функция для получения данных с Binance API
def get_binance_klines(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': int(start_time.timestamp() * 1000),
        'endTime': int(end_time.timestamp() * 1000),
        'limit': 1000
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Ошибка API: {response.status_code}, {response.text}")
        return None
    data = response.json()
    if not data:
        print("Данные не получены!")
        return None
    
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

# Функция расчета цены ликвидации
def calc_liquidation_price(entry_price, leverage, is_long=True):
    if is_long:
        return entry_price * (1 - 1 / leverage)
    else:
        return entry_price * (1 + 1 / leverage)

# Получение данных
current_time = datetime.utcnow()
yesterday_start = (current_time - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
yesterday_end = yesterday_start + timedelta(days=1) - timedelta(seconds=1)

print(f"Запрос данных с {yesterday_start} по {yesterday_end}")
df = get_binance_klines('BTCUSDT', '1h', yesterday_start, yesterday_end)

if df is None or df.empty:
    print("Ошибка: Данные не загружены!")
    exit()

print("Полученные данные (первые 5 строк):")
print(df.head())

# Нахождение точки отсчета
max_volume_row = df.loc[df['volume'].idxmax()]
entry_price = max_volume_row['close']
entry_volume = max_volume_row['volume']  # Объем торгов точки отсчета
max_volume_time = max_volume_row['open_time']
print(f"Точка отсчета: {max_volume_time}, Цена: {entry_price:.2f}, Объем: {entry_volume:.2f}")

# Расчет уровней ликвидации
leverages = [10, 25, 50]
liquidation_levels = []

colors = ['blue', 'green', 'purple']  # Цвета для x10, x25, x50 (один цвет для лонга и шорта каждого плеча)

for i, lev in enumerate(leverages):
    liq_long = calc_liquidation_price(entry_price, lev, True)
    liq_short = calc_liquidation_price(entry_price, lev, False)
    volume = df['volume'].mean() * (lev / 10)
    liquidation_levels.append({'Price': liq_long, 'Type': 'Long', 'Leverage': lev, 'Volume': volume, 'Color': colors[i]})
    liquidation_levels.append({'Price': liq_short, 'Type': 'Short', 'Leverage': lev, 'Volume': volume, 'Color': colors[i]})

liq_df = pd.DataFrame(liquidation_levels)
print("Данные для графика:")
print(liq_df)

# Подготовка данных для графика
long_data = liq_df[liq_df['Type'] == 'Long'].sort_values('Leverage')
short_data = liq_df[liq_df['Type'] == 'Short'].sort_values('Leverage')

# Создание графика с Matplotlib
plt.figure(figsize=(12, 6))

# Лонги
for i, row in long_data.iterrows():
    plt.bar(row['Price'], row['Volume'], width=500, color=row['Color'], alpha=0.7)
    # Подпись сверху столбца: "Leverage x Type Price"
    plt.text(row['Price'], row['Volume'] + 100, f'{row["Leverage"]}x {row["Type"]}\n{int(row["Price"])}', 
             ha='center', va='bottom', color='black', fontsize=8)

# Шорты
for i, row in short_data.iterrows():
    plt.bar(row['Price'], row['Volume'], width=500, color=row['Color'], alpha=0.7)
    # Подпись сверху столбца: "Leverage x Type Price"
    plt.text(row['Price'], row['Volume'] + 100, f'{row["Leverage"]}x {row["Type"]}\n{int(row["Price"])}', 
             ha='center', va='bottom', color='black', fontsize=8)

# Линия точки отсчета
plt.axvline(x=entry_price, color='white', linestyle='--')

# Настройка графика
plt.title(f'Bitcoin Liquidation Map (Binance, BTCUSDT, 1h) - {max_volume_time.strftime("%Y-%m-%d %H:%M:%S")}, Max Volume Entry Price: {entry_price:.2f}, Volume: {entry_volume:.2f}')
plt.xlabel('Price Levels (USD)')
plt.ylabel('Volume (BTC)')
plt.grid(True, linestyle='--', alpha=0.5)

# Установка пределов оси X для лучшей читаемости
plt.xlim(min(liq_df['Price']) - 1000, max(liq_df['Price']) + 1000)

# Убрать легенду (уже убрана в предыдущей версии)
plt.legend().remove()

# Показать график
plt.tight_layout()
plt.show()

# Сохранение в файл
plt.savefig('liquidation_map.png')
print("График сохранен в 'liquidation_map.png'")