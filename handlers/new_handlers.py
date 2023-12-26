import datetime

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (Message, ReplyKeyboardRemove, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from keyboards import get_keyboard, get_filling_inline
from MiddleWares import SetTimebyHandMiddleWare
from handlers.session_db import SessionDB, Session
from My_token import TOKEN

bot = Bot(TOKEN)
SDB = SessionDB()


filler_router = Router()
filler_router.message.filter(F.chat.type == 'private')


async def greet_and_get_days(message: Message, session: Session):
    await message.answer(f"Привет, {session.admin}!")
    if session.filler.days:
        await message.answer("Формирую ведомость")
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, session.filler.days)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        if session.filler.behavior == 'for filling':
            await message.answer("Все заполнено!")
        elif session.filler.behavior == 'for correction':
            await message.answer("Нечего исправлять!")
        SDB.remove_recipient(message)
    print(session.filler.days)
    print(session.filler.behavior)


@filler_router.message(Command("fill"))
async def cmd_fill(message: Message):
    session = SDB.add_new_session_and_change_it(message, 'for filling')
    await greet_and_get_days(message, session)


@filler_router.message(Command("correct"))
async def cmd_correct(message: Message):
    session = SDB.add_new_session_and_change_it(message, 'for correction')
    await greet_and_get_days(message, session)


@filler_router.message(Command("sleep"))
async def cmd_sleep(message: Message):
    session = SDB.add_new_session_and_change_it(message, 'manually')
    message_day = datetime.datetime.now()
    message_time = message_day.time()
    #message_time = datetime.time(hour=11, minute=1)
    if message_time.hour in range(6, 21):
        category = session.filler.r_siesta
        new_value = '+'
    else:
        if message_time.hour in range(0, 6):
            message_time = datetime.time(hour=0, minute=0)
            message_day -= datetime.timedelta(days=1)

        category = session.filler.r_sleeptime
        new_value = datetime.time.strftime(message_time, '%H:%M')

    message_day = datetime.date.strftime(message_day, '%d.%m.%y')
    session.filler.change_a_day(message_day)
    session.filler.filtering_by(category=category)
    session.filler.get_cells_ser()
    session.filler.change_a_cell(category)
    session.filler.fill_the_cell(new_value)
    #print(message_day, category, new_value)
    #print(session.changed_date, session.filler.active_cell)
    #print(session.filler.already_filled_dict)
    #await finish_filling(message)


router2 = Router()
router2.message.filter(F.from_user.first_name.in_(SDB.db))
filler_router.include_router(router2)


async def get_categories_keyboard(message: Message):
    SDB.r = message.from_user.first_name
    answer = "Выберите категорию для заполнения"
    kb = ReplyKeyboardBuilder()
    keyboard = get_keyboard(kb, SDB.session.inlines)
    await message.answer(answer, reply_markup=keyboard)


@router2.message(F.func(
    lambda message: message.text in SDB.change_session(message).filler.days))
async def change_a_date(message: Message):
    s = SDB.change_session(message)
    answer = ['Обращаем внимание на отметки:',
              '"не мог" - не выполнил по объективой причине (напр.: погода, вонь, лихорадка)',
              '"забыл" - забыл какой была отметка']

    s.filler.change_a_day(message.text)
    s.filler.filtering_by(positions=True)
    s.filler.get_cells_ser()
    if not s.filler.unfilled_cells:
        await message.reply("Все заполнено!",
                            reply_markup=ReplyKeyboardRemove())
        s.filler.change_done_mark()
        s.filler.save_day_data()
        # сильно подумать надо, откуда, что берется. миррор в мире филлера, это другой миррор. Нужно видимо здесь
        # новый экземпляр создавать, чтобы воспользоваться записью данных по дате и  заполненности
        await cmd_fill(message, greet=False) # перезапускаем прогу
    else:
        SDB.session.get_inlines()
        await message.reply('\n'.join(answer))
        await get_categories_keyboard(message)
