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

# Функция для получения текущей цены BTCUSDT с Binance
def get_current_price(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        return float(response.json()['price'])
    else:
        print(f"Ошибка получения текущей цены: {response.status_code}, {response.text}")
        return None

# Функция расчета цены ликвидации
def calc_liquidation_price(entry_price, leverage, is_long=True):
    return entry_price * (1 - 1 / leverage) if is_long else entry_price * (1 + 1 / leverage)

# Получение данных
current_time = datetime.utcnow()
yesterday_start = (current_time - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
yesterday_end = yesterday_start + timedelta(days=1) - timedelta(seconds=1)

print(f"Запрос данных с {yesterday_start} по {yesterday_end}")
df = get_binance_klines('BTCUSDT', '1h', yesterday_start, yesterday_end)

if df is None or df.empty:
    print("Ошибка: Данные не загружены!")
    exit()

# Нахождение точки отсчета
max_volume_row = df.loc[df['volume'].idxmax()]
entry_price = max_volume_row['close']
entry_volume = max_volume_row['volume']  # Объем торгов точки отсчета
max_volume_time = max_volume_row['open_time']

# Получение текущей цены в реальном времени
current_price = get_current_price()
if current_price is None:
    exit()

# Расчет уровней ликвидации
leverages = [10, 25, 50]
liquidation_levels = []
colors = ['blue', 'green', 'purple']  # Цвета для x10, x25, x50

for i, lev in enumerate(leverages):
    liq_long = calc_liquidation_price(entry_price, lev, True)
    liq_short = calc_liquidation_price(entry_price, lev, False)
    volume = df['volume'].max() * 1.1  # Устанавливаем максимальный объем для сплошных полос
    liquidation_levels.append({'Price': liq_long, 'Type': 'Long', 'Leverage': lev, 'Volume': volume, 'Color': colors[i]})
    liquidation_levels.append({'Price': liq_short, 'Type': 'Short', 'Leverage': lev, 'Volume': volume, 'Color': colors[i]})

liq_df = pd.DataFrame(liquidation_levels)

# Подготовка данных для графика
long_data = liq_df[liq_df['Type'] == 'Long'].sort_values('Leverage')
short_data = liq_df[liq_df['Type'] == 'Short'].sort_values('Leverage')

# Создание графика
plt.figure(figsize=(6, 12))  

# Лонги
for _, row in long_data.iterrows():
    plt.barh(row['Price'], row['Volume'] / 2, height=500, color=row['Color'], alpha=0.7, left=0)
    plt.text(row['Volume'] / 4, row['Price'] - 100, f'{row["Leverage"]}x {row["Type"]} {int(row["Price"])}', 
             ha='center', va='center', color='black', fontsize=8, weight='bold')

# Шорты
for _, row in short_data.iterrows():
    plt.barh(row['Price'], row['Volume'] / 2, height=500, color=row['Color'], alpha=0.7, left=0)
    plt.text(row['Volume'] / 4, row['Price'] - 100, f'{row["Leverage"]}x {row["Type"]} {int(row["Price"])}', 
             ha='center', va='center', color='black', fontsize=8, weight='bold')

# Линия точки отсчета
plt.axhline(y=entry_price, color='blue', linestyle='--')
plt.text(plt.xlim()[1] * 0.95, entry_price - 200, f'Entry Price: {entry_price:.2f}', 
         ha='right', va='center', color='blue', fontsize=8)

# Линия текущей цены
plt.axhline(y=current_price, color='black', linestyle='--')
plt.text(plt.xlim()[1] * 0.95, current_price - 200, f'Current Price: {current_price:.2f}', 
         ha='right', va='center', color='black', fontsize=8)

# Настройки
plt.title(f'Bitcoin Liquidation Map (Binance, BTCUSDT, 1h) - {max_volume_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
          f'Max Volume Entry Price: {entry_price:.2f}, Volume: {entry_volume:.2f}', fontsize=10)
plt.ylabel('Price Levels (USD)')  
plt.xlabel('Volume (BTC)')
plt.grid(True, linestyle='--', alpha=0.5)

# Настройка оси Y справа
ax = plt.gca()
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()

# Установка пределов оси Y
plt.ylim(min(liq_df['Price']) - 1000, max(liq_df['Price']) + 1000)

# Убрать легенду
plt.legend().remove()

# Показать график
plt.tight_layout()
plt.show()

# Сохранение
plt.savefig('liquidation_map_vertical.png')
print("График сохранен в 'liquidation_map_vertical.png'")
