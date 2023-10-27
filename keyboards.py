from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_keyboard(keyboard, keys_list, rows=None):
    print(keys_list)
    for key in keys_list:
        print(key)
        keyboard.add(KeyboardButton(text=key))
    keyboard.add(KeyboardButton(text='завершить заполнение'))
    if rows:
        keyboard.adjust(rows)
    else:
        keyboard.adjust(4)
    return keyboard.as_markup(resize_keyboard=True)
