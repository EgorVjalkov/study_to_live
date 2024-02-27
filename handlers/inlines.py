from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from filler.vedomost_cell import VedomostCell
from handlers.session_db import Session
from handlers.row_len_analyzer import RowLenAnalyzer


class CategoryCallback(CallbackData, prefix='f.i.l.l', sep='_'):
    recipient: str
    category: str
    btn: str


def get_keys(session: Session,
             cell: VedomostCell) -> list:
    keys = cell.keys
    end_key = 'следующая' if session.inlines else 'завершить'

    if 'time' in cell.name and session.fill_today:
        keys.append('в койке!')

    if session.filler.behavior != 'coefs':
        keys.extend(['не мог', 'забыл', end_key])
    else:
        keys.append(end_key)

    return keys


def get_filling_inline(session: Session,
                       cell: VedomostCell) -> InlineKeyboardBuilder:

    inline = InlineKeyboardBuilder()
    keys = get_keys(session, cell)
    rows_list = RowLenAnalyzer(keys).create_row_container()

    for row in rows_list:
        cb_data_list = [CategoryCallback(recipient=session.user, category=cell.name, btn=k)
                        for k in row]
        callbacks = [InlineKeyboardButton(text=cb.btn, callback_data=cb.pack()) for cb in cb_data_list]
        inline.row(*callbacks)

    return inline
