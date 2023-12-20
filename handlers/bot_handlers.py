import datetime
import pandas as pd

from aiogram import Bot
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (Message, ReplyKeyboardRemove, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from keyboards import get_keyboard, get_filling_inline
from MiddleWares import SetTimebyHandMiddleWare
from handlers.UserDB import UserDataBase
from My_token import TOKEN

bot = Bot(TOKEN)
UDB = UserDataBase()


filler_router = Router()
filler_router.message.filter(F.chat.type == 'private')


@filler_router.message(Command("fill"))
async def cmd_fill(message: Message, greet=True):
    UDB.add_new_recipient(message, behavior='for filling')
    if UDB.r_data.filler.days:
        answer = "Привет! Формирую ведомость" if greet else "Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, UDB.r_data.filler.days)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Все заполнено!")
        UDB.remove_recipient(message)


@filler_router.message(Command("correct"))
async def cmd_correct(message: Message):
    UDB.add_new_recipient(message, behavior='for correction')
    UDB.r_data.filler.limiting('for correction')
    if UDB.r_data.filler.days:
        answer = "Привет! Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, UDB.r_data.filler.days)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Нечего исправлять!")
        UDB.remove_recipient(message)


@filler_router.message(Command("sleep"))
async def cmd_sleep(message: Message):
    UDB.add_new_recipient(message, behavior='manually')
    message_day = datetime.datetime.now()
    message_time = message_day.time()
    #message_time = datetime.time(hour=11, minute=1)
    if message_time.hour in range(6, 21):
        category = UDB.r_data.filler.r_siesta
        new_value = '+'
    else:
        if message_time.hour in range(0, 6):
            message_time = datetime.time(hour=0, minute=0)
            message_day -= datetime.timedelta(days=1)

        category = UDB.r_data.filler.r_sleeptime
        new_value = datetime.time.strftime(message_time, '%H:%M')

    message_day = datetime.date.strftime(message_day, '%d.%m.%y')
    UDB.r_data.filler.change_a_day(message_day)
    UDB.r_data.filler.filtering_by(category=category)
    UDB.r_data.filler.get_cells_ser()
    UDB.r_data.filler.fill_the_cell(new_value)
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
    if UDB.r_data.filler.already_filled_dict:
        filled_for_answer = [f'За {UDB.r_data.filler.changed_date} Вы заполнили:']
        filled_for_answer.extend(UDB.r_data.filler.filled_cells_list_for_print)
        answer = "\n".join(filled_for_answer)
        UDB.r_data.filler.collect_data_to_day_row()

        if UDB.r_data.filler.is_filled:
            UDB.r_data.filler.save_day_data_to_mother_frame()
        else:
            UDB.r_data.filler.save_day_data_to_temp_db()
        print(pd.Series(UDB.r_data.filler.already_filled_dict))
        # нужен тестинг записи фреймов, потом чтение надо наладить

    UDB.remove_recipient(message)
    await message.answer(f'Завершeно! {answer}', reply_markup=ReplyKeyboardRemove())


async def get_categories_keyboard(message: Message):
    UDB.r = message.from_user.first_name
    answer = "Выберите категорию для заполнения"
    kb = ReplyKeyboardBuilder()
    keyboard = get_keyboard(kb, UDB.r_data.inlines)
    await message.answer(answer, reply_markup=keyboard)


@router2.message(F.func(
    lambda message: message.text in UDB.db[message.from_user.first_name].filler.days))
async def change_a_date(message: Message):
    UDB.r = message.from_user.first_name
    answer = ['Обращаем внимание на отметки:',
              '"не мог" - не выполнил по объективой причине (напр.: погода, вонь, лихорадка)',
              '"забыл" - забыл какой была отметка']

    UDB.r_data.filler.change_a_day(message.text)
    print(UDB.rows_in_process)
    print(UDB.r_data.is_date_busy(UDB.rows_in_process))
    if UDB.r_data.is_date_busy(UDB.rows_in_process):
        UDB.r_data.filler.filtering_by(only_private_categories=True)
        answer.append(f'Доступны только личные категории на данный момент')
    else:
        UDB.r_data.filler.filtering_by(positions=True)

    UDB.r_data.filler.get_cells_ser()

    if not UDB.r_data.filler.unfilled_cells:
        await message.reply("Все заполнено!",
                            reply_markup=ReplyKeyboardRemove())
        UDB.r_data.filler.change_done_mark()
        UDB.r_data.filler.save_day_data_to_mother_frame()
        await cmd_fill(message, greet=False) # перезапускаем прогу
    else:
        UDB.r_data.get_inlines()
        await message.reply('\n'.join(answer))
        await get_categories_keyboard(message)


@router2.message(F.func(
    lambda message: message.text in UDB.db[message.from_user.first_name].inlines))
async def change_a_category(message: Message):
    UDB.r = message.from_user.first_name
    cell_name = message.text
    UDB.r_data.inlines.remove(cell_name)
    cell_data = UDB.r_data.filler.cells_ser[cell_name]

    answer = cell_data['description']
    if not answer:
        answer = 'Нажмите кнопку на экране'
    else:
        answer = '\n'.join(answer)

    callback = InlineKeyboardBuilder()
    inline_args = UDB.r, callback, cell_name, cell_data['keys'], 'следующая'
    if not UDB.r_data.inlines:
        inline_args = UDB.r, callback, cell_name, cell_data['keys'], 'завершить'
    callback = get_filling_inline(*inline_args)

    if UDB.r_data.filler.behavior == 'for correction':
        await message.answer(f'Принято. Предыдущие значение - {cell_data["old_value"]}',
                             reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Принято', reply_markup=ReplyKeyboardRemove())

    await message.answer(answer, reply_markup=callback.as_markup())
    UDB.r_data.set_last_message(message)


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
        await get_categories_keyboard(UDB.r_data.last_message)
    elif 'завершить' in cat_value:
        await finish_filling(UDB.r_data.last_message)
    else:
        UDB.r_data.filler.change_a_cell(cat_name)
        if 'вручную' in cat_value and 'sleeptime' in cat_name:
            await remove_keyboard_if_sleeptime(UDB.r_data.last_message)
        else:
            UDB.r_data.filler.fill_the_cell(cat_value)
            await callback.answer(f"Вы заполнили '{cat_value}' в {UDB.r_data.filler.active_cell}")
        print(UDB.r)
        print(UDB.r_data.filler.active_cell)
        print(UDB.r_data.filler.already_filled_dict)


date_fill_router = Router()
date_fill_router.message.filter(F.func(
    lambda message: 'time' in UDB.db[message.from_user.first_name].filler.active_cell))
router3.include_router(date_fill_router)


@date_fill_router.message(
        F.text.func(lambda text: len(text) == 5 and text.find(':') == 2))
async def fill_a_cell_with_time(message: Message):
    UDB.r = message.from_user.first_name
    cat_value = message.text
    UDB.r_data.filler.fill_the_cell(cat_value)
    await message.answer(f"Вы заполнили '{cat_value}' в {UDB.r_data.filler.active_cell}")
    print(UDB.r)
    print(UDB.r_data.filler.active_cell)
    print(UDB.r_data.filler.already_filled_dict)
