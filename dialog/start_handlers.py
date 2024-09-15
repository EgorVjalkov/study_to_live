import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot
from aiogram_dialog import DialogManager, StartMode
from dialog.states import FillingVedomost

from My_token import TOKEN, ADMIN_ID
from filler.vedomost_filler import VedomostFiller, CoefsFiller, VedomostCounter
from filler.day_row import DayRow
from filler.date_funcs import today_for_filling
from DB_main import mirror


username_dict = {'Jegor': 'Egr', 'Валерия': 'Lera'}
bot = Bot(TOKEN)
filler_router = Router()


@filler_router.message(Command('fill'))
async def start_dialog(message: Message, dialog_manager: DialogManager):
    recipient = username_dict[message.from_user.first_name]
    await dialog_manager.start(FillingVedomost.date_menu,
                               mode=StartMode.RESET_STACK,
                               data={'filler': VedomostFiller(recipient, 'filling').__call__()},
                               )


@filler_router.message(Command('correct'))
async def start_dialog(m: Message, dialog_manager: DialogManager):
    recipient = username_dict[m.from_user.first_name]
    await dialog_manager.start(FillingVedomost.date_menu,
                               mode=StartMode.RESET_STACK,
                               data={'filler': VedomostFiller(recipient, 'correction').__call__()},
                               )


@filler_router.message(Command('count'))
async def start_dialog(m: Message, dialog_manager: DialogManager):
    recipient = username_dict[m.from_user.first_name]
    await dialog_manager.start(FillingVedomost.date_menu,
                               mode=StartMode.RESET_STACK,
                               data={'filler': VedomostCounter(recipient).__call__()},
                               )


@filler_router.message(Command('coefs'))
async def start_dialog(m: Message, dialog_manager: DialogManager):
    rec_data = m.from_user
    if rec_data.id != ADMIN_ID:
        await m.reply('Только Егорок шарит в коеффициентах, тебе оно надо???')
        return

    rec_name = username_dict[rec_data.first_name]
    await dialog_manager.start(FillingVedomost.date_menu,
                               mode=StartMode.RESET_STACK,
                               data={'filler': CoefsFiller(rec_name).__call__()},
                               )


@filler_router.message(Command('sleep'))
async def start_dialog(message: Message, dialog_manager: DialogManager):
    recipient = username_dict[message.from_user.first_name]
    message_day = today_for_filling() # <- date сохраняется после полуночи, чтобы писаться в соотв. ячейку
    message_time = datetime.datetime.now().time() #  а не другого числа
    print(message_day, message_time, 'inside func')

    if message_time.hour in range(6, 21):
        category = f'{recipient[0].lower()}:siesta'
        new_value = '+'
    else:
        category = f'{recipient[0].lower()}:sleeptime'
        new_value = datetime.time.strftime(message_time, '%H:%M')

    day_row = DayRow(mirror.get_day_row(message_day))

    if day_row[category]:
        print(day_row[category], 'correction')
        filler = VedomostFiller(recipient, 'correction', day_data=day_row).__call__()
    else:
        print(day_row[category], 'filling')
        filler = VedomostFiller(recipient, 'filling', day_data=day_row).__call__()

    filler.filter_cells()
    filler.active_cell = category
    filler.fill_the_active_cell(new_value)

    await dialog_manager.start(FillingVedomost.report_menu,
                               mode=StartMode.RESET_STACK,
                               data={'filler': filler},
                               )
