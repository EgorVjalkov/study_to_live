from aiogram.types import KeyboardButton, InlineKeyboardButton
from filler.vedomost_cell import VedomostCell
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from handlers.session_db import Session


def get_keyboard(keyboard, keys_list, rows=None):
    for key in keys_list:
        keyboard.add(KeyboardButton(text=key))
    if rows:
        keyboard.adjust(rows)
    else:
        keyboard.adjust(4)
    return keyboard.as_markup(resize_keyboard=True)


def get_filling_inline(inline: InlineKeyboardBuilder,
                       session: Session,
                       r_from_tg: str,
                       cell: VedomostCell):
    r = r_from_tg
    name = cell.name
    keys = cell.keys
    end_key = 'следующая' if session.inlines else 'завершить'
    if session.filler.behavior != 'coefs':
        keys.extend(['не мог', 'забыл', end_key])
    else:
        keys.append(end_key)

    keys = [InlineKeyboardButton(text=str(i), callback_data=f'fill_{r}_{name}_{i}')
            for i in cell.keys]
    inline.row(*keys)
    return inline
