from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot_main import filler, username_dict
from keyboards import get_keyboard, get_filling_inline


deleted_messages_list = []
router = Router()
# надо потестироваь на предмет асинхронности, почитать всякое про асунх
# запуск filler должен быть асинхронным!!!!
# подумай как очистить все поля и заново перезапустить филлер


@router.message(Command("start"))
async def cmd_start_and_get_r_vedomost(message: Message, great=True):
    r_name = username_dict[message.from_user.first_name]
    filler.get_r_name_and_limiting(r_name)
    # здесь слетает фильтрация глючит и позволяет предавать дату за все дни
    #filler.refresh_day_row()

    if filler.days_for_filling:
        answer = "Привет! Формирую ведомость" if great else "Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, filler.days_for_filling)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Все заполнено!")


async def get_categories_keyboard(message: Message):
    kb = ReplyKeyboardBuilder()
    keyboard = get_keyboard(kb, filler.non_filled_names_list)
    await message.answer("Выберите категорию для заполнения", reply_markup=keyboard)


@router.message(F.text.func(lambda text: text in filler.days_for_filling))
async def change_a_date(message: Message):
    filler.change_the_day_row(message.text)
    filler.filtering_by_positions()
    filler.get_non_filled_cells_df()
    if not filler.non_filled_names_list:
        await message.reply("Все заполнено!",
                            reply_markup=ReplyKeyboardRemove())

        filler.change_done_mark_and_save_day_data()
        await cmd_start_and_get_r_vedomost(message, great=False) # перезапускаем прогу

    else:
        await get_categories_keyboard(message)


router2 = Router()


@router2.message(F.text.func(lambda text: text in filler.non_filled_names_list))
async def change_a_category(message: Message):
    cell_name = message.text
    cell_data = filler.non_filled_cells_df[cell_name]

    answer = cell_data['description']
    if not answer:
        answer = 'Нажмите кнопку на экране'
    else:
        answer = '\n'.join(answer)

    callback = InlineKeyboardBuilder()
    callback = get_filling_inline(callback, cell_name, cell_data['keys'])
    await message.answer(answer, reply_markup=callback.as_markup())
    await get_categories_keyboard(message)


@router2.message(F.text == 'завершить заполнение')
async def finish_filling_by_message(message: Message):
    answer = 'Вы ничего не заполнили'
    if filler.day_row_index and filler.filled_names_list:
        filled_for_answer = [f'За {filler.changed_date} Вы заполнили:']
        filled_for_answer.extend(filler.filled_names_list)
        answer = "\n".join(filled_for_answer)
        filler.write_day_data_to_mother_frame()
        filler.change_done_mark_and_save_day_data()
        filler.refresh_day_row()
    await message.answer(f'Завершeно! {answer}', reply_markup=ReplyKeyboardRemove())


router3 = Router()


@router3.callback_query(F.data.contains('fill_'))
async def fill_the_cell(callback: CallbackQuery):
    call_data = callback.data.split('_')[1:]
    cat_name, cat_value = call_data[0], call_data[1]
    if 'вручную' in cat_value:
        filler.change_a_cell(cat_name)
        await callback.answer(f"Жду сообщение в формате ЧЧ:ММ")
    else:
        filler.change_a_cell(cat_name)
        filler.fill_the_cell(cat_value)
        await callback.answer(f"Вы заполнили {cat_value} в {filler.active_cell}")
        print(filler.non_filled_cells_df[filler.active_cell])
        print(filler.filled_names_list)


@router3.message(F.text.func(lambda text: ':' in text))
async def fill_a_cell_with_time(message: Message):
    cat_value = message.text
    filler.fill_the_cell(cat_value)
    await message.answer(f"Вы заполнили {cat_value} в {filler.active_cell}")
    print(filler.non_filled_cells_df[filler.active_cell])
    print(filler.filled_names_list)
