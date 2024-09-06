from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚘 Калькулятор", callback_data="calculation_start")],
        [InlineKeyboardButton(text="💰 Узнать курс", callback_data="get_course")]
    ])


back_button = InlineKeyboardButton(text="Назад", callback_data="back_to_start")


def add_back_button(keyboard):
    keyboard.inline_keyboard.append([back_button])
    return keyboard
