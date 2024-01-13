from aiogram.types import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup
from filler.vedomost_cell import VedomostCell
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from handlers.session_db import Session


def get_keyboard(keys_list, rows=None) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    for key in keys_list:
        keyboard.add(KeyboardButton(text=key))
    if rows:
        keyboard.adjust(rows)
    else:
        keyboard.adjust(5)
    return keyboard.as_markup(resize_keyboard=True)


def get_filling_inline(session: Session,
                       cell: VedomostCell) -> InlineKeyboardBuilder:
    inline = InlineKeyboardBuilder()
    r = session.user
    name = cell.name
    keys = cell.keys
    end_key = 'следующая' if session.inlines else 'завершить'
    if session.filler.behavior != 'coefs':
        keys.extend(['не мог', 'забыл', end_key])
    else:
        keys.append(end_key)

    keys = [InlineKeyboardButton(text=str(i), callback_data=f'fill_{r}_{name}_{i}')
            for i in keys]

    max_in_row = 5
    if len(keys) % max_in_row > 0:
        groups = len(keys) // max_in_row + 1
    else:
        groups = len(keys) // max_in_row
    group_keys_list = []
    for i in range(1, groups+1):
        group_keys_list.append(keys[:max_in_row])
        keys = [i for i in keys if keys.index(i) >= max_in_row]

    for g in group_keys_list:
        inline.row(*g)
    return inline


#max_in_row = 5
#keys = list(range(0, 18, 1))
#if len(keys) % max_in_row > 0:
#    groups = len(keys) // max_in_row + 1
#else:
#    groups = len(keys) // max_in_row
#group_keys_list = []
#for i in range(1, groups+1):
#    group_keys_list.append(keys[:max_in_row])
#    keys = [i for i in keys if keys.index(i) >= max_in_row]
#
#print(group_keys_list)
