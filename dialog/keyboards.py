from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dialog.row_len_analyzer import RowLenAnalyzer


def get_keyboard(keys_list) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    button_rows = RowLenAnalyzer(keys_list).create_row_container()

    for row in button_rows:
        row = [KeyboardButton(text=k) for k in row]
        keyboard.row(*row)

    return keyboard.as_markup(resize_keyboard=True)
