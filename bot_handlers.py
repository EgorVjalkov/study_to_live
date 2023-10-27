from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot_main import filler, username_dict
from keyboards import get_keyboard


router = Router()
# надо потестироваь на предмет асинхронности, почитать всякое про асунх
# запуск filler должен быть асинхронным!!!!
# подумай как очистить все поля и заново перезапустить филлер
# доделай с solid категориями


@router.message(Command("start"))
async def cmd_start_and_get_r_vedomost(message: Message, great=True):
    r_name = username_dict[message.from_user.first_name]
    filler.get_r_name_and_limiting(r_name)
    filler.refresh_day_row()

    if filler.days_for_filling:
        answer = "Привет! Формирую ведомость" if great else "Формирую ведомость"
        await message.answer(answer)
        days_kb = ReplyKeyboardBuilder()
        days_kb = get_keyboard(days_kb, filler.days_for_filling)
        await message.answer("Дата?", reply_markup=days_kb)
    else:
        await message.answer("Привет! Все заполнено!")


async def get_a_cell_keyboard(message: Message):
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
        # утро вечера мудренее липкая херня, не понимаю почему в строителя для клавф попадает серия
        await get_a_cell_keyboard(message) # клавиатура с категориями


router2 = Router()


@router2.message(Command("fill"))
async def get_a_cell_keyboard(message: Message):
    if not filler.day_row_index:
        await message.reply("Сначала нужно выбрать дату! Дайте команду /start")
    else:
        kb = ReplyKeyboardBuilder()
        keyboard = get_keyboard(kb, filler.r_cats_ser_by_positions)
        await message.answer("Выберите категорию для заполнения", reply_markup=keyboard)


def get_filling_inline(inline, cat_keys):
    if cat_keys:
        keys = [InlineKeyboardButton(text=str(i), callback_data=f'fill_{i}') for i in cat_keys]
        inline.row(*keys)

    inline.row(InlineKeyboardButton(text='не мог', callback_data='fill_не мог'),
               InlineKeyboardButton(text='забыл', callback_data='fill_забыл'))
    # надо красивое тут сдлать!
    return inline


@router2.message(F.text.func(lambda text: text in filler.r_cats_ser_by_positions))
async def change_a_category(message: Message):
    if filler.r_cats_ser_by_positions:
        cell.cat_name = message.text

        answer = cell.description
        if not cell.keys:
            answer.append("Напишите сообщение в формате: чч:мм или нaжмите кнопку на экране")

        if not answer:
            answer = 'Нажмите кнопку на экране'
        else:
            answer = '\n'.join(answer)

        callback = InlineKeyboardBuilder()
        callback = get_filling_inline(callback, cell.keys)
        await message.answer(answer, reply_markup=callback.as_markup())

        filler.filled[cell.cat_name] = None
        filler.r_cats_ser_by_positions.remove(message.text)

        kb = ReplyKeyboardBuilder()
        keyboard = get_categories_keyboard(kb, filler.r_cats_ser_by_positions)

        #здесь хотелочь бы при наличии отклика на колбэк вернуть новую клаву Надо мутить с асинхронью
        await message.answer("Следующая категория?", reply_markup=keyboard)
    else:
        await message.reply('Все заполнено!', reply_markup=ReplyKeyboardRemove())


@router2.message(F.text == 'завершить заполнение')
async def finish_filling_by_message(message: Message):
    answer = 'Вы ничего не заполнили'
    if filler.day_row_index:
        filled_in_str = ', '.join(filler.filled_names_list)
        if filled_in_str:
            answer = f'Вы заполнили {filled_in_str}'
            filler.write_day_data_to_mother_frame()
            filler.get_r_name_and_limiting()
    await message.answer(f'Завершeно! {answer}', reply_markup=ReplyKeyboardRemove())


router3 = Router()


@router3.callback_query(F.data.contains('fill_'))
async def fill_a_cell(callback: CallbackQuery):
    cat_value = callback.data.split('_')[1]
    print(cat_value)
    filled_cat = filler.fill_the_cell(cat_value) # здесь надо придумать, как перзаполнять категории
    print(filler.filled)
    print(filler.recipient_all_filled_flag)
    await callback.answer(f"Вы заполнили {cat_value} в {filled_cat}")


@router3.message(F.text.func(lambda text: ':' in text))
async def fill_a_cell_with_time(message: Message):
    filled_cat = filler.fill_the_cell(message.text)
    print(filler.filled)
    print(filler.recipient_all_filled_flag)
    if filled_cat:
        await message.answer(f"Вы заполнили {filled_cat}")
