from aiogram.fsm.state import StatesGroup, State


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
