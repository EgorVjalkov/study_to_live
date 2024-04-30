import datetime
import emoji

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram import Bot

from DB_main import mirror
from My_token import TOKEN
from handlers.session_db import SessionDB, Session
from handlers.keyboards import get_keyboard
from handlers.inlines import get_filling_inline, CategoryCallback
from filler.vedomost_cell import VedomostCell
from filler.manual_filling_cells import manual_filling_cells


bot = Bot(TOKEN)
SDB = SessionDB()


filler_router = Router()
filler_router.message.filter(F.chat.type == 'private')


async def greet_and_get_days(message: Message, session: Session):
    await message.answer(f"Привет, {session.user}!")
    if session.filler.days:
        await message.answer("Формирую ведомость")
        days_kb = get_keyboard(session.filler.days)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        if session.filler.behavior == 'filling':
            await message.answer("Все заполнено!")
        elif session.filler.behavior == 'correction':
            await message.answer("Нечего исправлять!")
        SDB.remove_recipient(message)
    print(session.filler.days)
    print(session.filler.behavior)
    print(SDB)


@filler_router.message(Command("fill"))
async def cmd_fill(message: Message):
    session = SDB.add_new_session_and_checkout(message, 'filling')
    await greet_and_get_days(message, session)


@filler_router.message(Command("correct"))
async def cmd_correct(message: Message):
    session = SDB.add_new_session_and_checkout(message, 'correction')
    await greet_and_get_days(message, session)


@filler_router.message(Command("coefs"))
async def cmd_coefs(message: Message):
    if SDB.is_superuser(message):
        session = SDB.add_new_session_and_checkout(message, 'coefs')
        await greet_and_get_days(message, session)
    else:
        await message.reply('Только Егорок шарит в коеффициентах, тебе оно надо???')


@filler_router.message(Command("sleep"))
async def cmd_sleep(message: Message,
                    sleep_time: datetime.datetime = None):

    if not sleep_time:
        sleep_time = datetime.datetime.now()
        s = SDB.add_new_session_and_checkout(message, 'manually')
    else:
        s = SDB.switch_session(by_message=message)
    print(SDB)
    print(sleep_time)

    if SDB.is_date_busy(sleep_time.date()):
        await message.reply('Запомнил, запишу, когда это станет возможным')
        await SDB.date_dispatcher(sleep_time.date(), cmd_sleep, *(message, sleep_time))
    else:
        s.manually_fill_sleep_time(sleep_time)
        await finish_filling(message)


router2 = Router()
router2.message.filter(F.from_user.first_name.in_(SDB.db))
filler_router.include_router(router2)


@router2.message(Command("finish"))
async def finish_filling(message: Message):
    s = SDB.switch_session(by_message=message)

    if s.filler.already_filled_dict:
        s.filler.collect_data_to_day_row()
        mirror.save_day_data(s.filler.day)
        print(s.filler.already_filled_dict)
        answer = s.get_answer_if_finish()
    else:
        answer = 'Вы ничего не заполнили'

    await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    if s.filler.sleeptime_is_empty:
        await message.answer('Не забудь команду /sleep, когда соберешься ' + emoji.emojize(':sleeping_face:'))

    if not SDB.is_superuser(message):
        await bot.send_message(SDB.superuser_id, f'{s.user} завершил заполнение. {answer}')

    print(SDB)
    SDB.remove_recipient(message)
    print(SDB)


async def get_categories_keyboard(message: Message, s: Session):
    if s.filler.behavior == 'coefs':
        acc_answer = '\n'.join(s.filler.acc_in_str)
        await message.reply(acc_answer)
    answer = "Выберите категорию"
    keyboard = get_keyboard(s.inlines)
    await message.answer(answer, reply_markup=keyboard)


@router2.message(F.func(
    lambda message: message.text in SDB.switch_session(message).filler.days))
async def change_a_date(message: Message):
    s = SDB.switch_session(by_message=message)
    if SDB.is_date_busy(message.text):
        await message.reply('Заполнение невозможно, Строка занята.',
                            reply_markup=ReplyKeyboardRemove())
        await SDB.date_dispatcher(message.text, change_a_date, message)

    else:
        s.filler.change_a_day(message.text)
        s.filler.get_cells_ser()
        if not s.filler.unfilled_cells:
            await message.reply("Все заполнено!",
                                reply_markup=ReplyKeyboardRemove())
            s.filler.change_done_mark()
            mirror.save_day_data(s.filler.day)
        else:
            s.get_inlines()
            await get_categories_keyboard(message, s)
            SDB.refresh_session(s)
            print(SDB)


@router2.message(F.func(
    lambda message: message.text in SDB.switch_session(message).inlines))
async def change_a_category(message: Message):
    s = SDB.switch_session(by_message=message)
    cell_name = message.text
    s.inlines.remove(cell_name)
    cell_data: VedomostCell = s.filler.cells_ser[cell_name]

    callback = get_filling_inline(s, cell_data)
    await message.answer(cell_data.print_old_value_by(s.filler.behavior),
                         reply_markup=ReplyKeyboardRemove())
    await message.answer(cell_data.print_description(),
                         reply_markup=callback.as_markup())
    s.set_last_message(message)
    SDB.refresh_session(s)


router3 = Router()
router3.callback_query.filter(
    F.data.func(lambda data: data.split('_')[1:][0] in SDB.db))
router2.include_router(router3)


async def remove_keyboard_if_manually(message: Message, session: Session):
    if session.filler.behavior == 'coefs':
        answer = f"Жду данные о {session.filler.active_cell}"
    else:
        answer = f"Жду сообщение в формате ЧЧ:ММ"
    await message.answer(answer,
                         reply_markup=ReplyKeyboardRemove())


@router3.callback_query(F.data.contains(CategoryCallback.__prefix__))
async def fill_by_callback(callback: CallbackQuery):

    call_data = callback.data.split('_')[1:]
    s = SDB.switch_session(by_name=call_data[0])
    cat_name, cat_value = call_data[1], call_data[2]

    if 'следующая' in cat_value:
        await get_categories_keyboard(s.last_message, s)

    elif 'завершить' in cat_value:
        await finish_filling(s.last_message)

    else:
        s.filler.change_a_cell(cat_name)

        if 'вручную' in cat_value:
            await remove_keyboard_if_manually(s.last_message, s)

        else:

            if 'в койке!' in cat_value:
                message_time = datetime.datetime.now().time()
                cat_value = datetime.time.strftime(message_time, '%H:%M')
                s.filler.fill_the_cell(cat_value)

            else:
                s.filler.fill_the_cell(cat_value)
                SDB.refresh_session(s)

            await callback.answer(f"Вы заполнили '{cat_value}' в {s.filler.active_cell}")
        print(SDB.r)
        print(s.filler.active_cell)
        print(s.filler.already_filled_dict)


manually_fill_router = Router()
manually_fill_router.message.filter(F.func(
    lambda message: SDB.switch_session(by_message=message).filler.active_cell in manual_filling_cells))
router3.include_router(manually_fill_router)


#@manually_fill_router.message(
#    F.text.func(lambda text: len(text) == 5 and text.find(':') == 2))


@manually_fill_router.message()
async def fill_a_cell_with_time(message: Message):
    s = SDB.switch_session(by_message=message)
    cat_value = message.text
    s.filler.fill_the_cell(cat_value)
    SDB.refresh_session(s)
    await message.answer(f"Вы заполнили '{cat_value}' в {s.filler.active_cell}")
    print(SDB.r)
    print(s.filler.active_cell)
    print(s.filler.already_filled_dict)
