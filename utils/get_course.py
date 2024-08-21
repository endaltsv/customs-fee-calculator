import requests
from bs4 import BeautifulSoup
import yfinance as yf

from bot.config import URL_COURSES


async def parse_atb_bank():
    url = URL_COURSES
    response = requests.get(url)
    result = ''

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        currency_table = soup.find('div', class_='currency-table')
        rows = currency_table.find_all('div', class_='currency-table__tr')

        for row in rows[1:]:
            columns = row.find_all('div', class_='currency-table__td')
            currency_name = columns[0].text.strip().replace('ЗА', ' ЗА')
            buy_rate = columns[1].text.strip()
            sell_rate = columns[2].text.strip()

            result += f"\n\n{currency_name}: Покупка: {buy_rate}, Продажа: {sell_rate}"
    else:
        result = f"Не удалось получить данные. Код статуса: {response.status_code}"

    return result


def parse_yfinance():
    try:
        cny_rub = yf.Ticker("CNYRUB=X")
        jpy_rub = yf.Ticker("JPYRUB=X")

        hist = cny_rub.history(period="1d")
        hist2 = jpy_rub.history(period="1d")

        rate = hist['Close'].iloc[-1]
        rate2 = hist2['Close'].iloc[-1]

        print(f"CNY ЗА 1¥: {rate}")
        print(f"JPY ЗА 1¥: {rate2}")

    except Exception as e:
        print(f"Ошибка получения курса: {e}")
        return None
