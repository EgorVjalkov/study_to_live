from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot_main import filler, username_dict
from keyboards import get_keyboard, get_filling_inline
from MiddleWares import SetTimebyHandMiddleWare


inlines = []
msg_del = [] # лист для удаления сообщений
last_message = None
# надо потестироваь на предмет асинхронности, почитать всякое про асунх
# запуск filler должен быть асинхронным!!!!
# подумай как очистить все поля и заново перезапустить филлер

router = Router()
router.message.filter(F.chat.type == 'private')


@router.message(Command("start"))
async def cmd_start_and_get_r_vedomost(message: Message, greet=True):
    print(message.chat.type)
    r_name = username_dict[message.from_user.first_name]
    filler.get_r_name_and_limiting(r_name)
    #filler.refresh_day_row()

    if filler.days_for_filling:
        answer = "Привет! Формирую ведомость" if greet else "Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, filler.days_for_filling)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Все заполнено!")


async def get_categories_keyboard(message: Message):
    if inlines:
        answer = "Выберите категорию для заполнения"
    else:
        answer = 'Завершите заполнение'
    kb = ReplyKeyboardBuilder()
    keyboard = get_keyboard(kb, inlines)
    await message.answer(answer, reply_markup=keyboard)


@router.message(F.text.func(lambda text: text in filler.days_for_filling))
async def change_a_date(message: Message):
    filler.change_the_day_row(message.text)
    filler.filtering_by_positions()
    filler.get_non_filled_cells_df()
    if not filler.non_filled_names_list:
        await message.reply("Все заполнено!",
                            reply_markup=ReplyKeyboardRemove())

        filler.change_done_mark_and_save_day_data()
        await cmd_start_and_get_r_vedomost(message, greet=False) # перезапускаем прогу

    else:
        inlines.extend(filler.non_filled_names_list)
        answer = ['Обращаем внимание на отметки:',
                  '"не мог" - не выполнил по объективой причине (напр.: погода, вонь, лихорадка)',
                  '"забыл" - забыл какой была отметка']
        await message.reply('\n'.join(answer))
        await get_categories_keyboard(message)


router2 = Router()


@router2.message(F.text.func(lambda text: text in inlines))
async def change_a_category(message: Message):
    cell_name = message.text
    inlines.remove(cell_name)
    cell_data = filler.non_filled_cells_df[cell_name]

    answer = cell_data['description']
    if not answer:
        answer = 'Нажмите кнопку на экране'
    else:
        answer = '\n'.join(answer)

    callback = InlineKeyboardBuilder()
    inline_args = callback, cell_name, cell_data['keys'], 'следующая'
    if not inlines:
        inline_args = callback, cell_name, cell_data['keys'], 'завершить'

    callback = get_filling_inline(*inline_args)
    await message.answer(f'{cell_name}:', reply_markup=ReplyKeyboardRemove())
    await message.answer(answer, reply_markup=callback.as_markup())
    global last_message
    last_message = message


@router2.message(F.text == 'завершаю')
async def finish_filling(message: Message):
    answer = 'Вы ничего не заполнили'
    if isinstance(filler.day_row_index, int) and filler.filled_names_list:
        filled_for_answer = [f'За {filler.changed_date} Вы заполнили:']
        filled_for_answer.extend(filler.filled_names_list)
        answer = "\n".join(filled_for_answer)
        filler.write_day_data_to_mother_frame()
        filler.change_done_mark_and_save_day_data()
        filler.refresh_day_row()
        inlines.clear()
    await message.answer(f'Завершeно! {answer}\n Жмите /start, чтобы продолжить', reply_markup=ReplyKeyboardRemove())


router3 = Router()


async def remove_keyboard_if_sleeptime(message: Message):
    await message.answer(f"Жду сообщение в формате ЧЧ:ММ",
                         reply_markup=ReplyKeyboardRemove())


@router3.callback_query(F.data.contains('fill_'))
async def fill_by_callback(callback: CallbackQuery):
    call_data = callback.data.split('_')[1:]
    cat_name, cat_value = call_data[0], call_data[1]
    filler.change_a_cell(cat_name)

    if 'следующая' in cat_value:
        await get_categories_keyboard(last_message)
    elif 'завершить' in cat_value:
        await finish_filling(last_message)
    elif 'вручную' in cat_value and 'sleeptime' in cat_name:
        await remove_keyboard_if_sleeptime(last_message)
    else:
        filler.fill_the_cell(cat_value)
        await callback.answer(f"Вы заполнили '{cat_value}' в {filler.active_cell}")
    print(filler.non_filled_cells_df[filler.active_cell])
    print(filler.filled_names_list)


date_fill_router = Router()
# не понимаю как это работает!
date_fill_router.message.middleware(SetTimebyHandMiddleWare(filler.active_cell))


@date_fill_router.message(F.text.func(lambda text: len(text) == 5 and text.find(':') == 2)) # чч:mm
async def fill_a_cell_with_time(message: Message):
    cat_value = message.text
    filler.fill_the_cell(cat_value)
    await message.answer(f"Вы заполнили '{cat_value}' в {filler.active_cell}")
    await get_categories_keyboard(message)
    print(filler.non_filled_cells_df[filler.active_cell])
    print(filler.filled_names_list)

