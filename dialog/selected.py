from typing import Optional

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Cancel, Button, SwitchTo
from aiogram_dialog.widgets.input.text import TextInput
from aiogram_dialog.api.exceptions import NoContextError

from filler.vedomost_filler import VedomostFiller, BusyError
from filler.vedomost_cell import VedomostCell
from dialog.states import FillingVedomost


def get_filler(dm: DialogManager) -> Optional[VedomostFiller]: # подумай, может сдесь можно get
    try:
        ctx = dm.current_context()
        return ctx.start_data['filler']
    except NoContextError:
        return None


def set_filler(dm: DialogManager, filler: VedomostFiller) -> None:
    ctx = dm.current_context()
    ctx.start_data.update({'filler': filler})


async def on_chosen_date(c: CallbackQuery,
                         w: Select,
                         dm: DialogManager,
                         item_id: str,
                         **kwargs) -> None: # рефактор
    
    filler: VedomostFiller = get_filler(dm)
    try:
        filler.change_a_day(item_id)
        set_filler(dm, filler)
        filler.get_cells_ser()
        await dm.switch_to(FillingVedomost.category_menu)
    except BusyError:
        # здесь можно добавить другое сообщение при одной занятой дате
        await dm.event.answer('В данный момент строка занята, выберите другую дату или завершите сеанс')


async def on_chosen_category(c: CallbackQuery,
                             w: Select,
                             dm: DialogManager,
                             item_id: str,
                             **kwargs) -> None:  # рефактор

    filler: VedomostFiller = get_filler(dm)
    filler.change_a_cell(item_id)
    set_filler(dm, filler)
    await dm.switch_to(FillingVedomost.filling_menu)


