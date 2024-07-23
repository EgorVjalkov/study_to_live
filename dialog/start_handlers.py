import datetime
import emoji

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram import Bot
from aiogram_dialog import DialogManager, StartMode
from dialog.states import FillingVedomost, FillingSleeptime

from DB_main import mirror
from My_token import TOKEN, ADMIN_ID
from dialog.keyboards import get_keyboard
from dialog.inlines import get_filling_inline, CategoryCallback
from filler.vedomost_filler import VedomostFiller
from filler.vedomost_cell import VedomostCell
from filler.manual_filling_cells import manual_filling_cells


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


@filler_router.message(Command('coefs'))
async def start_dialog(m: Message, dialog_manager: DialogManager):
    rec_data = m.from_user
    if rec_data.id != ADMIN_ID:
        await m.reply('Только Егорок шарит в коеффициентах, тебе оно надо???')
        return

    rec_name = username_dict[rec_data.first_name]
    await dialog_manager.start(FillingVedomost.date_menu,
                               mode=StartMode.RESET_STACK,
                               data={'filler': VedomostFiller(rec_name, 'coefs').__call__()},
                               )


@filler_router.message(Command('sleep'))
async def start_dialog(m: Message, dm: DialogManager):
    recipient = username_dict[m.from_user.first_name]
    now = datetime.datetime.now()
    await dm.start(FillingSleeptime.report_menu,
                   mode=StartMode.RESET_STACK,
                   data={'filler': VedomostFiller(recipient, 'manually').__call__(),
                         'now': now},
                   )
