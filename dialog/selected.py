from typing import Optional
from datetime import datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Cancel, Button, SwitchTo
from aiogram_dialog.widgets.input.text import TextInput
from aiogram_dialog.api.exceptions import NoContextError

from DB_main import mirror
from temp_db.mirror_db import BusyError
from filler.vedomost_filler import VedomostFiller
from filler.vedomost_cell import VedomostCell
from dialog.kbs import SCROLLING_HEIGHT
from dialog.states import FillingVedomost


def get_filler(dm: DialogManager) -> Optional[VedomostFiller]: # подумай, может сдесь можно get
    try:
        ctx = dm.current_context()
        return ctx.start_data['filler']
    except NoContextError:
        return None


async def go_to_category_menu(tgo: TelegramObject,
                              dm: DialogManager,
                              ** kwargs) -> None:

    filler: VedomostFiller = get_filler(dm)
    if filler.need_to_fill > SCROLLING_HEIGHT:
        await dm.switch_to(FillingVedomost.category_menu_if_scroll)  #############
    else:
        await dm.switch_to(FillingVedomost.category_menu_if_simple)  #############


async def on_chosen_date(c: CallbackQuery,
                         w: Select,
                         dm: DialogManager,
                         item_id: str,
                         **kwargs) -> None:
    
    filler: VedomostFiller = get_filler(dm)
    try:
        filler.change_day(item_id)
        # если каунтер то филтер селлс не надо
        if filler.behavior == 'count':
            await dm.switch_to(FillingVedomost.report_menu)
        else:
            filler.filter_cells()
            mirror.occupy(filler.day.name)
            await go_to_category_menu(c, dm)
    except BusyError:
        await c.answer('Cтрока занята, выберите другую дату или завершите сеанс')
    except BaseException as error:
        await c.answer(f'ошибка {error}')
        mirror.set_day_status(filler.day)


async def on_back_to_date_menu(c: CallbackQuery,
                               w: SwitchTo,
                               dm: DialogManager,
                               ** kwargs) -> None:

    filler: VedomostFiller = get_filler(dm)
    mirror.set_day_status(filler.day)


async def on_chosen_category(c: CallbackQuery,
                             w: Select,
                             dm: DialogManager,
                             item_id: str,
                             **kwargs) -> None:  # рефактор

    filler: VedomostFiller = get_filler(dm)
    filler.active_cell = item_id
    await dm.switch_to(FillingVedomost.filling_menu)


async def on_back_to_category_menu(c: CallbackQuery,
                                   w: Button,
                                   dm: DialogManager,
                                   ** kwargs) -> None:
    await go_to_category_menu(c, dm)


async def on_filling_category(c: CallbackQuery,
                              w: Select,
                              dm: DialogManager,
                              item_id: str,
                              **kwargs) -> None:

    if item_id == 'вручную':
        await dm.switch_to(FillingVedomost.filling_by_kb)
        return

    filler: VedomostFiller = get_filler(dm)

    if item_id == 'сейчас!':
        message_time = datetime.now().time()
        cat_value = message_time.strftime('%H:%M')
        filler.fill_the_active_cell(cat_value)

    else:
        filler.fill_the_active_cell(item_id)

    print(filler.working_space)
    await go_to_category_menu(c, dm)


async def on_filling_by_kb(m: Message,
                           w: TextInput,
                           dm: DialogManager,
                           input_data: str,
                           **kwargs) -> None:
    filler: VedomostFiller = get_filler(dm)
    filler.fill_the_active_cell(input_data)
    await go_to_category_menu(m, dm)


