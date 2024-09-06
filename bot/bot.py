from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot.config import TOKEN

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()
