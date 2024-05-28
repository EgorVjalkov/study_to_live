from aiogram.fsm.state import StatesGroup, State


class FillingVedomost(StatesGroup):
    date_menu = State()
    category_menu = State()
    filling_menu = State()
    report_menu = State()


class FillingSleeptime(StatesGroup):
    report_menu = State()
