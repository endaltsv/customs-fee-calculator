import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.get_course import parse_atb_bank
from bot.bot import bot
from bot.config import PUBLIC_CHAT_ID, THREAD_ID

logger = logging.getLogger(__name__)


async def schedule_send_course():
    try:
        course = await parse_atb_bank()
        await bot.send_message(chat_id=PUBLIC_CHAT_ID, text=course, message_thread_id=THREAD_ID)
    except Exception as e:
        logger.error(f"Ошибка при отправке курса валют: {e}")


async def send_course(message):
    try:
        course = await parse_atb_bank()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_to_start")]
        ])
        await bot.send_message(chat_id=message.chat.id, text=course, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при отправке курса валют: {e}")
