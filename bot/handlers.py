import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.bot import dp
from bot.keyboards import get_main_menu_keyboard
from bot.states import CalculatorState
from services.course_service import send_course
from services.calculator_service import start_calculation_handler

from services.calculator_service import (
    process_age, process_price, process_dtype, process_pwr,
    process_obyem, process_pwr_val, process_hybrid1, process_hybrid2,
    ask_lico, process_lico
)

logger = logging.getLogger(__name__)


@dp.message(Command("start"))
async def start(message: types.Message):
    try:
        keyboard = get_main_menu_keyboard()
        await message.answer("<b>👋 Приветствую </b>", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")
        await message.answer("Произошла ошибка при запуске бота.")


@dp.callback_query(lambda c: c.data == "back_to_start")
async def back_handler(callback_query: types.CallbackQuery):
    await start(callback_query.message)
    return


@dp.callback_query(lambda c: c.data == "get_course")
async def get_course(callback_query: types.CallbackQuery):
    await send_course(callback_query.message)


@dp.callback_query(lambda c: c.data == "calculation_start")
async def start_calculation(callback_query: types.CallbackQuery, state: FSMContext):
    await start_calculation_handler(callback_query, state)


@dp.callback_query(CalculatorState.age)
async def handle_age(callback_query: types.CallbackQuery, state: FSMContext):
    await process_age(callback_query, state)


@dp.message(CalculatorState.price)
async def handle_price(message: types.Message, state: FSMContext):
    await process_price(message, state)


@dp.callback_query(CalculatorState.dtype)
async def handle_dtype(callback_query: types.CallbackQuery, state: FSMContext):
    await process_dtype(callback_query, state)


@dp.callback_query(CalculatorState.pwr)
async def handle_pwr(callback_query: types.CallbackQuery, state: FSMContext):
    await process_pwr(callback_query, state)


@dp.message(CalculatorState.obyem)
async def handle_obyem(message: types.Message, state: FSMContext):
    await process_obyem(message, state)


@dp.message(CalculatorState.pwr_val)
async def handle_pwr_val(message: types.Message, state: FSMContext):
    await process_pwr_val(message, state)


@dp.callback_query(CalculatorState.hybrid1)
async def handle_hybrid1(callback_query: types.CallbackQuery, state: FSMContext):
    await process_hybrid1(callback_query, state)


@dp.callback_query(CalculatorState.hybrid2)
async def handle_hybrid2(callback_query: types.CallbackQuery, state: FSMContext):
    await process_hybrid2(callback_query, state)


@dp.callback_query(CalculatorState.lico)
async def handle_lico(callback_query: types.CallbackQuery, state: FSMContext):
    await process_lico(callback_query, state)
