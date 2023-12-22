import datetime
import pandas as pd

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (Message, ReplyKeyboardRemove, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from keyboards import get_keyboard, get_filling_inline
from MiddleWares import SetTimebyHandMiddleWare
from handlers.UserDB import SessionDB, Session
from My_token import TOKEN
from vedomost_filler import VedomostFiller

bot = Bot(TOKEN)
UDB = SessionDB()


filler_router = Router()
filler_router.message.filter(F.chat.type == 'private')


@filler_router.message(Command("fill"))
async def cmd_fill(message: Message, greet=True):
    s = Session(message, 'for filling')
    if s.filler.days:
        answer = "Привет! Формирую ведомость" if greet else "Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, s.filler.days)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Все заполнено!")
        UDB.remove_recipient(message)


router2 = Router()
router2.message.filter(F.from_user.first_name.in_(UDB.db))
filler_router.include_router(router2)


async def get_categories_keyboard(message: Message):
    UDB.r = message.from_user.first_name
    answer = "Выберите категорию для заполнения"
    kb = ReplyKeyboardBuilder()
    keyboard = get_keyboard(kb, UDB.session.inlines)
    await message.answer(answer, reply_markup=keyboard)


@router2.message(F.func(
    lambda message: message.text in UDB.db[message.from_user.first_name].filler.days))
async def change_a_date(message: Message):
    UDB.r = message.from_user.first_name
    answer = ['Обращаем внимание на отметки:',
              '"не мог" - не выполнил по объективой причине (напр.: погода, вонь, лихорадка)',
              '"забыл" - забыл какой была отметка']

    UDB.session.filler.change_a_day(message.text)
    print(UDB.dates_in_process)
    print(UDB.session.is_date_busy(UDB.dates_in_process))
    if UDB.session.is_date_busy(UDB.dates_in_process):
        UDB.session.filler.filtering_by(only_private_categories=True)
        answer.append(f'Доступны только личные категории на данный момент')
    else:
        UDB.session.filler.filtering_by(positions=True)

    UDB.session.filler.get_cells_ser()

    if not UDB.session.filler.unfilled_cells:
        await message.reply("Все заполнено!",
                            reply_markup=ReplyKeyboardRemove())
        UDB.session.filler.change_done_mark()
        UDB.session.filler.save_day_data_to_mother_frame()
        await cmd_fill(message, greet=False) # перезапускаем прогу
    else:
        UDB.session.get_inlines()
        await message.reply('\n'.join(answer))
        await get_categories_keyboard(message)
