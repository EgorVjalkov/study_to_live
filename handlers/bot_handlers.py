import datetime
import pandas as pd

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (Message, ReplyKeyboardRemove, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from keyboards import get_keyboard, get_filling_inline
from MiddleWares import SetTimebyHandMiddleWare
from handlers.session_db import SessionDB
from My_token import TOKEN

bot = Bot(TOKEN)
UDB = SessionDB()


filler_router = Router()
filler_router.message.filter(F.chat.type == 'private')


@filler_router.message(Command("fill"))
async def cmd_fill(message: Message, greet=True):
    UDB.add_new_session(message, behavior='for filling')
    if UDB.session.filler.days:
        answer = "Привет! Формирую ведомость" if greet else "Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, UDB.session.filler.days)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Все заполнено!")
        UDB.remove_recipient(message)


@filler_router.message(Command("correct"))
async def cmd_correct(message: Message):
    UDB.add_new_session(message, behavior='for correction')
    UDB.session.filler.limiting('for correction')
    if UDB.session.filler.days:
        answer = "Привет! Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, UDB.session.filler.days)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Нечего исправлять!")
        UDB.remove_recipient(message)


@filler_router.message(Command("sleep"))
async def cmd_sleep(message: Message):
    UDB.add_new_session(message, behavior='manually')
    message_day = datetime.datetime.now()
    message_time = message_day.time()
    #message_time = datetime.time(hour=11, minute=1)
    if message_time.hour in range(6, 21):
        category = UDB.session.filler.r_siesta
        new_value = '+'
    else:
        if message_time.hour in range(0, 6):
            message_time = datetime.time(hour=0, minute=0)
            message_day -= datetime.timedelta(days=1)

        category = UDB.session.filler.r_sleeptime
        new_value = datetime.time.strftime(message_time, '%H:%M')

    message_day = datetime.date.strftime(message_day, '%d.%m.%y')
    UDB.session.filler.change_a_day(message_day)
    UDB.session.filler.filtering_by(category=category)
    UDB.session.filler.get_cells_ser()
    UDB.session.filler.fill_the_cell(new_value)
    #print(message_day, category, new_value)
    #print(UDB.r_data.filler.active_cell)
    #print(UDB.r_data.filler.already_filled_dict)
    await finish_filling(message)


router2 = Router()
router2.message.filter(F.from_user.first_name.in_(UDB.db))
filler_router.include_router(router2)


@router2.message(Command("finish"))
async def finish_filling(message: Message):
    UDB.r = message.from_user.first_name
    answer = 'Вы ничего не заполнили'
    if UDB.session.filler.already_filled_dict:
        filled_for_answer = [f'За {UDB.session.filler.changed_date} Вы заполнили:']
        filled_for_answer.extend(UDB.session.filler.filled_cells_list_for_print)
        answer = "\n".join(filled_for_answer)
        UDB.session.filler.collect_data_to_day_row()

        if UDB.session.filler.is_filled:
            UDB.session.filler.save_day_data_to_mother_frame()
        else:
            UDB.session.filler.save_day_data_to_temp_db()
        print(pd.Series(UDB.session.filler.already_filled_dict))
        # нужен тестинг записи фреймов, потом чтение надо наладить

    UDB.remove_recipient(message)
    await message.answer(f'Завершeно! {answer}', reply_markup=ReplyKeyboardRemove())


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


@router2.message(F.func(
    lambda message: message.text in UDB.db[message.from_user.first_name].inlines))
async def change_a_category(message: Message):
    UDB.r = message.from_user.first_name
    cell_name = message.text
    UDB.session.inlines.remove(cell_name)
    cell_data = UDB.session.filler.cells_ser[cell_name]

    answer = cell_data['description']
    if not answer:
        answer = 'Нажмите кнопку на экране'
    else:
        answer = '\n'.join(answer)

    callback = InlineKeyboardBuilder()
    inline_args = UDB.r, callback, cell_name, cell_data['keys'], 'следующая'
    if not UDB.session.inlines:
        inline_args = UDB.r, callback, cell_name, cell_data['keys'], 'завершить'
    callback = get_filling_inline(*inline_args)

    if UDB.session.filler.behavior == 'for correction':
        await message.answer(f'Принято. Предыдущие значение - {cell_data["old_value"]}',
                             reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Принято', reply_markup=ReplyKeyboardRemove())

    await message.answer(answer, reply_markup=callback.as_markup())
    UDB.session.set_last_message(message)


router3 = Router()
router3.callback_query.filter(
    F.data.func(lambda data: data.split('_')[1:][0] in UDB.db))
router2.include_router(router3)


async def remove_keyboard_if_sleeptime(message: Message):
    await message.answer(f"Жду сообщение в формате ЧЧ:ММ",
                         reply_markup=ReplyKeyboardRemove())


@router3.callback_query(F.data.contains('fill_'))
async def fill_by_callback(callback: CallbackQuery):
    call_data = callback.data.split('_')[1:]
    UDB.r = call_data[0]
    cat_name, cat_value = call_data[1], call_data[2]

    if 'следующая' in cat_value:
        await get_categories_keyboard(UDB.session.last_message)
    elif 'завершить' in cat_value:
        await finish_filling(UDB.session.last_message)
    else:
        UDB.session.filler.change_a_cell(cat_name)
        if 'вручную' in cat_value and 'sleeptime' in cat_name:
            await remove_keyboard_if_sleeptime(UDB.session.last_message)
        else:
            UDB.session.filler.fill_the_cell(cat_value)
            await callback.answer(f"Вы заполнили '{cat_value}' в {UDB.session.filler.active_cell}")
        print(UDB.r)
        print(UDB.session.filler.active_cell)
        print(UDB.session.filler.already_filled_dict)


date_fill_router = Router()
date_fill_router.message.filter(F.func(
    lambda message: 'time' in UDB.db[message.from_user.first_name].filler.active_cell))
router3.include_router(date_fill_router)


@date_fill_router.message(
        F.text.func(lambda text: len(text) == 5 and text.find(':') == 2))
async def fill_a_cell_with_time(message: Message):
    UDB.r = message.from_user.first_name
    cat_value = message.text
    UDB.session.filler.fill_the_cell(cat_value)
    await message.answer(f"Вы заполнили '{cat_value}' в {UDB.session.filler.active_cell}")
    print(UDB.r)
    print(UDB.session.filler.active_cell)
    print(UDB.session.filler.already_filled_dict)
