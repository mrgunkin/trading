import requests
import pandas as pd
import telegram
from io import BytesIO

# Настройки
TELEGRAM_BOT_TOKEN = ""
CHAT_ID = ""
XLS_URL = "https://www.ishares.com/us/products/333011/fund/1521942788811.ajax?fileType=xls&fileName=iShares-Bitcoin-Trust-ETF_fund&dataType=fund"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/html",
    "Referer": "https://www.ishares.com/",
}

def download_xls(url):
    """Скачивает XLS-файл"""
    session = requests.Session()
    response = session.get(url, headers=HEADERS, allow_redirects=True)

    if response.status_code == 200:
        content = response.content

        # Проверяем, HTML ли это
        if content.startswith(b"<!DOCTYPE html") or b"<html" in content[:500]:
            with open("debug.html", "wb") as f:
                f.write(content)
            raise Exception("Сайт вернул HTML, сохранено в debug.html")

        return BytesIO(content)
    else:
        raise Exception(f"Ошибка скачивания: {response.status_code}")

def parse_holdings(xls_data):
    """Читает данные из диапазона A8:G10 на 2-й странице"""
    df = pd.read_excel(xls_data, sheet_name=1, header=None, engine="xlrd")  # Читаем без заголовков
    df = df.iloc[7:10, 0:7]  # Берем строки 8-10 и столбцы A-G
    return df

def send_to_telegram(df):
    """Отправляет таблицу в Telegram"""
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    text = df.to_string(index=False, header=False)  # Без индексов и заголовков

    bot.send_message(chat_id=CHAT_ID, text=f"📊 Данные из XLS:\n```\n{text}\n```", parse_mode="Markdown")

def main():
    try:
        xls_data = download_xls(XLS_URL)
        df = parse_holdings(xls_data)
        send_to_telegram(df)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
