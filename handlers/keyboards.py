from aiogram.types import KeyboardButton, InlineKeyboardButton
from filler.vedomost_cell import VedomostCell
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_keyboard(keyboard, keys_list, rows=None):
    for key in keys_list:
        keyboard.add(KeyboardButton(text=key))
    if rows:
        keyboard.adjust(rows)
    else:
        keyboard.adjust(4)
    return keyboard.as_markup(resize_keyboard=True)


def get_filling_inline(inline: InlineKeyboardBuilder, cell: VedomostCell, inlines: list):
    r = cell.recipient
    name = cell.name
    end_key = 'следующая' if inlines else 'завершить'
    if cell.keys:
        keys = [InlineKeyboardButton(text=str(i),
                                     callback_data=f'fill_{r}_{name}_{i}')
                for i in cell.keys]
        inline.row(*keys)

    inline.row(InlineKeyboardButton(text='не мог', callback_data=f'fill_{r}_{name}_не мог'),
               InlineKeyboardButton(text='забыл', callback_data=f'fill_{r}_{name}_забыл'),
               InlineKeyboardButton(text=end_key, callback_data=f'fill_{r}_{name}_{end_key}'))
    return inline
