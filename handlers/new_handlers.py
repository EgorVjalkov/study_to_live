import datetime

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (Message, ReplyKeyboardRemove, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from async_func import time_awaiting
from handlers.keyboards import get_keyboard, get_filling_inline
from handlers.session_db import SessionDB, Session
from My_token import TOKEN
from DB_main import mirror
from filler.vedomost_cell import VedomostCell

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
    print(SDB)


@filler_router.message(Command("fill"))
async def cmd_fill(message: Message):
    session = SDB.add_new_session_and_change_it(message, 'for filling')
    await greet_and_get_days(message, session)


@filler_router.message(Command("correct"))
async def cmd_correct(message: Message):
    session = SDB.add_new_session_and_change_it(message, 'for correction')
    await greet_and_get_days(message, session)


@filler_router.message(Command("sleep"))
async def cmd_sleep(message: Message,
                    await_mode: bool = False,
                    now: datetime.datetime = None):
    if not now:
        now = datetime.datetime.now()
    if SDB.is_date_busy(now.date()):
        if not await_mode:
            await message.reply("Запомнил! Запишу, когда это станет возможным",
                                reply_markup=ReplyKeyboardRemove())
        await time_awaiting(cmd_sleep, (message, True, now), 10)
    else:
        s = SDB.add_new_session_and_change_it(message, 'manually')
        s.manually_fill_sleep_time(now)
        await finish_filling(message)


router2 = Router()
router2.message.filter(F.from_user.first_name.in_(SDB.db))
filler_router.include_router(router2)


@router2.message(Command("finish"))
async def finish_filling(message: Message):
    s = SDB.change_session(by_message=message)
    answer = 'Вы ничего не заполнили'
    if s.filler.already_filled_dict:
        filled_for_answer = [f'За {s.filler.date_to_str} заполнено:']
        filled_for_answer.extend(s.filler.filled_cells_list_for_print)
        answer = "\n".join(filled_for_answer)
        s.filler.collect_data_to_day_row()
        mirror.save_day_data(s.filler.day)
        print(s.filler.already_filled_dict)
    SDB.remove_recipient(message)
    await message.answer(f'Завершeно! {answer}', reply_markup=ReplyKeyboardRemove())
    if s.admin_id != SDB.superuser_id:
        await bot.send_message(SDB.superuser_id, f'{s.admin} завершил заполнение. {answer}')


async def get_categories_keyboard(message: Message):
    SDB.r = message.from_user.first_name
    answer = "Выберите категорию для заполнения"
    kb = ReplyKeyboardBuilder()
    keyboard = get_keyboard(kb, SDB.session.inlines)
    await message.answer(answer, reply_markup=keyboard)


@router2.message(F.func(
    lambda message: message.text in SDB.change_session(message).filler.days))
async def change_a_date(message: Message, await_mode=False):
    is_busy = SDB.is_date_busy(message.text)
    if is_busy:
        if not await_mode:
            await message.reply("Заполнение ведомости на эту дату в процессе. Я сообщу, когда это станет возможным",
                                reply_markup=ReplyKeyboardRemove())
        await time_awaiting(change_a_date, (message, True), 10)
    else:
        s = SDB.change_session(by_message=message)
        answer = ['Обращаем внимание на отметки:',
                  '"не мог" - не выполнил по объективой причине (напр.: погода, вонь, лихорадка)',
                  '"забыл" - забыл какой была отметка']
        s.filler.change_a_day(message.text)
        s.filler.get_cells_ser()
        SDB.refresh_session(s) # как это тестить???
        # делаем сначала на одного, потом задумаемся о многочеловековом заполнении
        if not s.filler.unfilled_cells:
            await message.reply("Все заполнено!",
                                reply_markup=ReplyKeyboardRemove())
            s.filler.change_done_mark()
            mirror.save_day_data(s.filler.day)
        else:
            s.get_inlines()
            await message.reply('\n'.join(answer))
            await get_categories_keyboard(message)
            print(SDB)


@router2.message(F.func(
    lambda message: message.text in SDB.change_session(message).inlines))
async def change_a_category(message: Message):
    s = SDB.change_session(by_message=message)
    cell_name = message.text
    s.inlines.remove(cell_name)
    cell_data: VedomostCell = s.filler.cells_ser[cell_name]

    callback = get_filling_inline(InlineKeyboardBuilder(), SDB.r, cell_data, s.inlines)
    await message.answer(cell_data.print_old_value_by(s.filler.behavior),
                         reply_markup=ReplyKeyboardRemove())
    await message.answer(cell_data.print_description(), reply_markup=callback.as_markup())
    s.set_last_message(message)
    SDB.refresh_session(s)


router3 = Router()
router3.callback_query.filter(
    F.data.func(lambda data: data.split('_')[1:][0] in SDB.db))
router2.include_router(router3)


async def remove_keyboard_if_sleeptime(message: Message):
    await message.answer(f"Жду сообщение в формате ЧЧ:ММ",
                         reply_markup=ReplyKeyboardRemove())


@router3.callback_query(F.data.contains('fill_'))
async def fill_by_callback(callback: CallbackQuery):
    call_data = callback.data.split('_')[1:]
    s = SDB.change_session(by_name=call_data[0])
    cat_name, cat_value = call_data[1], call_data[2]

    if 'следующая' in cat_value:
        await get_categories_keyboard(s.last_message)
    elif 'завершить' in cat_value:
        await finish_filling(s.last_message)
    else:
        s.filler.change_a_cell(cat_name)
        if 'вручную' in cat_value and 'sleeptime' in cat_name:
            await remove_keyboard_if_sleeptime(s.last_message)
        else:
            s.filler.fill_the_cell(cat_value)
            SDB.refresh_session(s)
            await callback.answer(f"Вы заполнили '{cat_value}' в {s.filler.active_cell}")

        print(SDB.r)
        print(s.filler.active_cell)
        print(s.filler.already_filled_dict)


date_fill_router = Router()
date_fill_router.message.filter(F.func(
    lambda message: 'time' in SDB.change_session(by_message=message).filler.active_cell))
router3.include_router(date_fill_router)


@date_fill_router.message(
    F.text.func(lambda text: len(text) == 5 and text.find(':') == 2))
async def fill_a_cell_with_time(message: Message):
    s = SDB.change_session(by_message=message)
    cat_value = message.text
    s.filler.fill_the_cell(cat_value)
    SDB.refresh_session(s)
    await message.answer(f"Вы заполнили '{cat_value}' в {s.filler.active_cell}")
    print(SDB.r)
    print(s.filler.active_cell)
    print(s.filler.already_filled_dict)
