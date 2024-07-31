from aiogram.fsm.state import StatesGroup, State


class FillingVedomost(StatesGroup):
    date_menu = State()

    category_menu_if_simple = State()
    category_menu_if_scroll = State()

    filling_menu = State()

    filling_by_kb = State()

    report_menu = State()


class FillingSleeptime(StatesGroup):
    report_menu = State()
