import aiohttp
import requests
from bs4 import BeautifulSoup
from bot.config import URL_COURSES


async def parse_atb_bank():
    result = ''
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL_COURSES) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    currency_table = soup.find('div', class_='currency-table')
                    rows = currency_table.find_all('div', class_='currency-table__tr')

                    for row in rows[1:]:
                        columns = row.find_all('div', class_='currency-table__td')
                        currency_name = columns[0].text.strip().replace('ЗА', ' ЗА')
                        buy_rate = columns[1].text.strip()
                        sell_rate = columns[2].text.strip()

                        result += f"\n\n{currency_name}: Покупка: {buy_rate}, Продажа: {sell_rate}"
                else:
                    result = f"Не удалось получить данные. Код статуса: {response.status}"
    except Exception as e:
        result = "Ошибка парсинга курса."

    return result

