import aiohttp
from aiocache import cached
from bs4 import BeautifulSoup
from bot.config import URL_COURSES, PROXY_URL, PROXY_USERNAME, PROXY_PASSWORD
import logging
from aiohttp import BasicAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@cached(ttl=600)
async def parse_atb_bank():
    result = ''
    proxy_url = PROXY_URL
    proxy_auth = BasicAuth(PROXY_USERNAME, PROXY_PASSWORD)

    try:
        logger.info("Начало запроса через прокси")
        async with aiohttp.ClientSession() as session:
            async with session.get(URL_COURSES, proxy=proxy_url, proxy_auth=proxy_auth) as response:
                logger.info(f"Код статуса: {response.status}")
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    currency_table = soup.find_all('div', class_='currency-table')
                    rows = currency_table[-2].find_all('div', class_='currency-table__tr')

                    for row in rows[1:]:
                        columns = row.find_all('div', class_='currency-table__td')
                        currency_name = columns[0].text.strip().replace('ЗА', ' ЗА')
                        buy_rate = columns[1].text.strip()
                        sell_rate = columns[2].text.strip()

                        result += f"\n\n{currency_name}: Покупка: {buy_rate}, Продажа: {sell_rate}"
                else:
                    result = f"Не удалось получить данные. Код статуса: {response.status}"
    except Exception as e:
        logger.error(f"Ошибка при запросе: {e}")
        result = "Ошибка парсинга курса."

    return result


async def test_proxy_connection():
    proxy_url = PROXY_URL
    proxy_auth = BasicAuth(PROXY_USERNAME, PROXY_PASSWORD)
    test_url = 'https://httpbin.org/ip'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, proxy=proxy_url, proxy_auth=proxy_auth) as response:
                if response.status == 200:
                    data = await response.json()
                    logging.info(f"IP через прокси: {data}")
                else:
                    logging.error(f"Ошибка. Код статуса: {response.status}")
    except Exception as e:
        logging.error(f"Ошибка при запросе: {e}")

