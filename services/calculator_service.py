import logging
import os

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from bot.bot import bot
from bot.states import CalculatorState
from bot.keyboards import add_back_button
from utils.get_price import get_price_and_create_image, create_payload

logger = logging.getLogger(__name__)


async def start_calculation_handler(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Менее 3 лет", callback_data="age0")],
            [InlineKeyboardButton(text="От 3 до 5 лет", callback_data="age3")],
            [InlineKeyboardButton(text="От 5 до 7 лет", callback_data="age5")],
            [InlineKeyboardButton(text="Более 7 лет", callback_data="age7")]
        ])
        keyboard = add_back_button(keyboard)
        await callback_query.message.answer("Выберите возраст автомобиля:", reply_markup=keyboard)
        await state.set_state(CalculatorState.age)
    except Exception as e:
        logger.error(f"Ошибка при запуске калькулятора: {e}")
        await callback_query.message.answer("Ошибка при запуске калькулятора.")


async def process_age(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(age=callback_query.data)
        await callback_query.message.answer("Введите цену автомобиля (в JPY):")
        await state.set_state(CalculatorState.price)
    except Exception as e:
        logger.error(f"Error processing age: {e}")
        await callback_query.message.answer("Ошибка при обработке возраста автомобиля.")


async def process_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)  # Преобразуем текст в число
        await state.update_data(price=price)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Бензиновый", callback_data="ben")],
            [InlineKeyboardButton(text="Дизельный", callback_data="dis")],
            [InlineKeyboardButton(text="Электрический", callback_data="electric")]
        ])
        keyboard = add_back_button(keyboard)
        await message.answer("Выберите тип двигателя:", reply_markup=keyboard)
        await state.set_state(CalculatorState.dtype)
    except ValueError:
        logger.warning(f"Invalid price entered: {message.text}")
        await message.answer("Ошибка: введите корректную цену (число).")
    except Exception as e:
        logger.error(f"Error processing price: {e}")
        await message.answer("Ошибка при обработке цены автомобиля.")


async def process_dtype(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(dtype=callback_query.data)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="л.с.", callback_data="ls")],
            [InlineKeyboardButton(text="кВт", callback_data="kvt")]
        ])
        keyboard = add_back_button(keyboard)
        await callback_query.message.answer("Выберите тип мощности (л.с. или кВт):", reply_markup=keyboard)
        await state.set_state(CalculatorState.pwr)
    except Exception as e:
        logger.error(f"Error processing engine type: {e}")
        await callback_query.message.answer("Ошибка при выборе типа двигателя.")


async def process_pwr(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(pwr=callback_query.data)
        await callback_query.message.answer("Введите объем двигателя в куб.см:")
        await state.set_state(CalculatorState.obyem)
    except Exception as e:
        logger.error(f"Error processing power type: {e}")
        await callback_query.message.answer("Ошибка при выборе типа мощности.")


async def process_obyem(message: types.Message, state: FSMContext):
    try:
        obyem = int(message.text)  # Преобразуем текст в число
        await state.update_data(obyem=obyem)
        await message.answer("Введите мощность двигателя:")
        await state.set_state(CalculatorState.pwr_val)
    except ValueError:
        logger.warning(f"Invalid engine volume entered: {message.text}")
        await message.answer("Ошибка: введите корректный объем двигателя (число).")
    except Exception as e:
        logger.error(f"Error processing engine volume: {e}")
        await message.answer("Ошибка при обработке объема двигателя.")


async def process_pwr_val(message: types.Message, state: FSMContext):
    try:
        pwr_val = int(message.text)  # Преобразуем текст в число
        await state.update_data(pwr_val=pwr_val)

        data = await state.get_data()
        if data['dtype'] != "electric":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Не гибрид", callback_data="1")],
                [InlineKeyboardButton(text="Электрогибрид", callback_data="2")],
                [InlineKeyboardButton(text="Электрогибрид(PHEV)", callback_data="3")]
            ])
            keyboard = add_back_button(keyboard)
            await message.answer("Выберите тип гибрида:", reply_markup=keyboard)
            await state.set_state(CalculatorState.hybrid1)
        else:
            await ask_lico(message, state)
    except ValueError:
        logger.warning(f"Invalid power value entered: {message.text}")
        await message.answer("Ошибка: введите корректную мощность двигателя (число).")
    except Exception as e:
        logger.error(f"Error processing engine power: {e}")
        await message.answer("Ошибка при обработке мощности двигателя.")


async def process_hybrid1(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        hybrid1 = callback_query.data
        await state.update_data(hybrid1=hybrid1)

        if hybrid1 != "1":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="ДВС > ЭД", callback_data="a")],
                [InlineKeyboardButton(text="ДВС < ЭД", callback_data="b")]
            ])
            keyboard = add_back_button(keyboard)
            await callback_query.message.answer("Выберите соотношение мощности ДВС и ЭД:", reply_markup=keyboard)
            await state.set_state(CalculatorState.hybrid2)
        else:
            await ask_lico(callback_query.message, state)
    except Exception as e:
        logger.error(f"Error processing hybrid type: {e}")
        await callback_query.message.answer("Ошибка при выборе типа гибрида.")


async def process_hybrid2(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(hybrid2=callback_query.data)
        await ask_lico(callback_query.message, state)
    except Exception as e:
        logger.error(f"Error processing hybrid power ratio: {e}")
        await callback_query.message.answer("Ошибка при выборе соотношения мощности гибрида.")


async def ask_lico(message: types.Message, state: FSMContext):
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Физическое лицо для ЛИЧНОГО пользования", callback_data="fiz_personal_use")],
            [InlineKeyboardButton(text="Юридическое лицо", callback_data="ur")]
        ])
        keyboard = add_back_button(keyboard)
        await message.answer("Выберите тип лица:", reply_markup=keyboard)
        await state.set_state(CalculatorState.lico)
    except Exception as e:
        logger.error(f"Error asking for legal entity: {e}")
        await message.answer("Ошибка при выборе типа лица.")


async def process_lico(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(lico=callback_query.data)

        data = await state.get_data()
        payload = create_payload(data)

        merged_image_path = get_price_and_create_image(payload)

        if not merged_image_path:
            await callback_query.message.answer("Ошибка при генерации изображения.")
            return

        photo = FSInputFile(merged_image_path)
        await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo)
        os.remove(merged_image_path)
        await state.clear()
    except FileNotFoundError as e:
        logger.error(f"Image file not found: {e}")
        await callback_query.message.answer("Ошибка: файл с изображением не найден.")
    except Exception as e:
        logger.error(f"Error processing legal entity: {e}")
        await callback_query.message.answer("Ошибка при выборе типа лица.")
