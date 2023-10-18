from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot_main import filler, cell, username_dict


router = Router()
# надо потестироваь на предмет асинхронности, почитать всякое про асунх
# запуск filler должен быть асинхронным!!!!
# подумай как очистить все поля и заново перезапустить филлер
# доделай с solid категориями


@router.message(Command("start"))
async def cmd_start_and_get_r_vedomost(message: Message):
    filler.r_name = username_dict[message.from_user.first_name]

    if filler.days_for_filling:
        await message.answer("Привет! Формирую ведомость")
        builder = ReplyKeyboardBuilder()

        for day in filler.days_for_filling:
            builder.add(KeyboardButton(text=day))
        builder.adjust(4)
        await message.answer("Дата?", reply_markup=builder.as_markup(resize_keyboard=True,
                                                                     input_field_placeholder="Выберите дату",
                                                                     ))
    else:
        await message.answer("Привет! Все заполнено!")


@router.message(F.text.func(lambda text: text in filler.days_for_filling))
async def change_a_date(message: Message):
    filler.change_the_day_row(message.text) # здесь мы уже лицезреем day_frame
    await message.reply(f"Принято. Чтоб передать данные, дайте команду /fill",
                        reply_markup=ReplyKeyboardRemove())


router2 = Router()


def get_categories_keyboard(keyboard, cat_list):
    for key in cat_list:
        keyboard.add(KeyboardButton(text=key))
    keyboard.add(KeyboardButton(text='завершить заполнение'))
    keyboard.adjust(4)
    return keyboard.as_markup(resize_keyboard=True)


@router2.message(Command("fill"))
async def get_a_cell_keyboard(message: Message):
    if filler.day_row.vedomost.empty:
        await message.reply("Сначала нужно выбрать дату! Дайте команду /start")
    else:
        filler.get_non_filled_categories()
        if not filler.non_filled_categories:
            await message.reply("Все заполнено!")
            # здесь нужна функция, которая поставит "Y" в ведомость. проверка на чухана (меня)
        else:
            kb = ReplyKeyboardBuilder()
            keyboard = get_categories_keyboard(kb, filler.non_filled_categories)
            await message.answer("Выберите категорию для заполнения", reply_markup=keyboard)


def get_filling_inline(inline, cat_keys):
    if cat_keys:
        keys = [InlineKeyboardButton(text=str(i), callback_data=f'fill_{i}') for i in cat_keys]
        inline.row(*keys)

    inline.row(InlineKeyboardButton(text='не мог', callback_data='fill_не мог'),
               InlineKeyboardButton(text='забыл', callback_data='fill_забыл'))
    # надо красивое тут сдлать!
    return inline


@router2.message(F.text.func(lambda text: text in filler.non_filled_categories))
async def change_a_category(message: Message):
    if filler.non_filled_categories:
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
        filler.non_filled_categories.remove(message.text)

        kb = ReplyKeyboardBuilder()
        keyboard = get_categories_keyboard(kb, filler.non_filled_categories)

        #здесь хотелочь бы при наличии отклика на колбэк вернуть новую клаву Надо мутить с асинхронью
        await message.answer("Следующая категория?", reply_markup=keyboard)
    else:
        await message.reply('Все заполнено!', reply_markup=ReplyKeyboardRemove())


@router2.message(F.text == 'завершить заполнение')
async def finish_filling_by_message(message: Message):
    filled_in_str = ', '.join(list(filler.filled.keys()))
    if filled_in_str:
        answer = f'Вы заполнили {filled_in_str}'
        filler.save_day_data()
        filler.get_mother_frame_and_refresh_values()
    else:
        answer = 'Вы ничего не заполнили'
    await message.answer(f'Завершeно! {answer}', reply_markup=ReplyKeyboardRemove())


router3 = Router()


@router3.callback_query(F.data.contains('fill_'))
async def fill_a_cell(callback: CallbackQuery):
    cat_value = callback.data.split('_')[1]
    print(cat_value)
    filled_cat = filler.fill_a_cell(cat_value) # здесь надо придумать, как перзаполнять категории
    print(filler.filled)
    print(filler.all_filled_flag)
    await callback.answer(f"Вы заполнили {cat_value} в {filled_cat}")


@router3.message(F.text.func(lambda text: ':' in text))
async def fill_a_cell_with_time(message: Message):
    filled_cat = filler.fill_a_cell(message.text)
    print(filler.filled)
    print(filler.all_filled_flag)
    if filled_cat:
        await message.answer(f"Вы заполнили {filled_cat}")

