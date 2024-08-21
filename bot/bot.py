import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from bot.config import TOKEN, PUBLIC_CHAT_ID, THREAD_ID
from utils.get_course import parse_atb_bank
from utils.get_price import create_payload, get_price_and_create_image

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


async def send_course():
    course = await parse_atb_bank()
    await bot.send_message(chat_id=PUBLIC_CHAT_ID, text=course,
                           message_thread_id=THREAD_ID)


class CalculatorState(StatesGroup):
    age = State()
    price = State()
    dtype = State()
    pwr = State()
    obyem = State()
    pwr_val = State()
    hybrid1 = State()
    hybrid2 = State()
    lico = State()


back_button = InlineKeyboardButton(text="Назад", callback_data="back_to_start")


def add_back_button(keyboard):
    keyboard.inline_keyboard.append([back_button])
    return keyboard



@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚘 Калькулятор", callback_data="calculation_start")],
        [InlineKeyboardButton(text="💰 Узнать курс", callback_data="get_course")]
    ])
    await message.answer("<b>👋 Приветствую </b>", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "get_course")
async def start_calculation(callback_query: types.CallbackQuery):
    course = await parse_atb_bank()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_start")],
    ])
    await callback_query.message.answer(course, keyboard=keyboard)


@dp.callback_query(lambda c: c.data == "calculation_start")
async def start_calculation(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Менее 3 лет", callback_data="age0")],
        [InlineKeyboardButton(text="От 3 до 5 лет", callback_data="age3")],
        [InlineKeyboardButton(text="От 5 до 7 лет", callback_data="age5")],
        [InlineKeyboardButton(text="Более 7 лет", callback_data="age7")]
    ])
    keyboard = add_back_button(keyboard)
    await callback_query.message.answer("Выберите возраст автомобиля:", reply_markup=keyboard)
    await state.set_state(CalculatorState.age)


@dp.callback_query(CalculatorState.age)
async def process_age(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_start":
        await start(callback_query.message)
        return

    await state.update_data(age=callback_query.data)
    await callback_query.message.answer("Введите цену автомобиля: (в JPY)")
    await state.set_state(CalculatorState.price)


@dp.message(CalculatorState.price)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Бензиновый", callback_data="ben")],
        [InlineKeyboardButton(text="Дизельный", callback_data="dis")],
        [InlineKeyboardButton(text="Электрический", callback_data="electric")]
    ])
    keyboard = add_back_button(keyboard)
    await message.answer("Выберите тип двигателя:", reply_markup=keyboard)
    await state.set_state(CalculatorState.dtype)


@dp.callback_query(CalculatorState.dtype)
async def process_dtype(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_start":
        await start(callback_query.message)
        return

    dtype = callback_query.data
    await state.update_data(dtype=dtype)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="л.с.", callback_data="ls")],
        [InlineKeyboardButton(text="кВт", callback_data="kvt")]
    ])
    keyboard = add_back_button(keyboard)
    await callback_query.message.answer("Выберите тип мощности (л.с. или кВт):", reply_markup=keyboard)
    await state.set_state(CalculatorState.pwr)


@dp.callback_query(CalculatorState.pwr)
async def process_pwr(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_start":
        await start(callback_query.message)
        return

    await state.update_data(pwr=callback_query.data)
    await callback_query.message.answer("Введите объем двигателя в куб.см:")
    await state.set_state(CalculatorState.obyem)


@dp.message(CalculatorState.obyem)
async def process_obyem(message: types.Message, state: FSMContext):
    await state.update_data(obyem=message.text)
    await message.answer("Введите мощность двигателя:")
    await state.set_state(CalculatorState.pwr_val)


@dp.message(CalculatorState.pwr_val)
async def process_pwr_val(message: types.Message, state: FSMContext):
    await state.update_data(pwr_val=message.text)

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


@dp.callback_query(CalculatorState.hybrid1)
async def process_hybrid1(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_start":
        await start(callback_query.message)
        return

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


@dp.callback_query(CalculatorState.hybrid2)
async def process_hybrid2(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_start":
        await start(callback_query.message)
        return

    await state.update_data(hybrid2=callback_query.data)
    await ask_lico(callback_query.message, state)


async def ask_lico(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Физическое лицо для ЛИЧНОГО пользования", callback_data="fiz_personal_use")],
        [InlineKeyboardButton(text="Юридическое лицо", callback_data="ur")]
    ])
    keyboard = add_back_button(keyboard)
    await message.answer("Выберите тип лица:", reply_markup=keyboard)
    await state.set_state(CalculatorState.lico)


@dp.callback_query(CalculatorState.lico)
async def process_lico(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_start":
        await start(callback_query.message)
        return

    await state.update_data(lico=callback_query.data)

    data = await state.get_data()
    payload = create_payload(data)

    merged_image_path = get_price_and_create_image(payload)

    if not os.path.exists(merged_image_path):
        raise FileNotFoundError(f"Файл {merged_image_path} не найден.")

    print(merged_image_path)
    photo = FSInputFile(merged_image_path)

    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo)
    os.remove(merged_image_path)

    await state.clear()
