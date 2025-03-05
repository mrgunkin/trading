import requests
import pandas as pd
from io import BytesIO

# Ссылка на файл
XLS_URL = "https://www.ishares.com/us/products/333011/fund/1521942788811.ajax?fileType=xls&fileName=iShares-Bitcoin-Trust-ETF_fund&dataType=fund"

# Заголовки для обхода защиты
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Referer": "https://www.ishares.com/",
}

def download_xls(url):
    """Скачивает файл и возвращает его содержимое"""
    response = requests.get(url, headers=HEADERS)
    return response.content  # XML-файл в виде байтов

def parse_xml(xml_data):
    """Парсит XML и выводит таблицы"""
    df = pd.read_xml(BytesIO(xml_data))  # Читаем XML
    return df

def main():
    xml_data = download_xls(XLS_URL)
    df = parse_xml(xml_data)
    print("📊 Данные из XML:\n", df.head())

if __name__ == "__main__":
    main()
