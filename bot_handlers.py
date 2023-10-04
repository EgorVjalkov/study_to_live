import time

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot_main import filler, username_dict


router = Router()
# надо потестироваь на предмет асинхронности, почитать всякое про асунх
# запуск filler должен быть асинхронным!!!!


@router.message(Command("start"))
async def cmd_start_and_get_r_vedomost(message: Message):
    filler.r_name = username_dict[message.from_user.first_name]
    print(filler.r_name)
    filler.get_r_vedomost()
    dayz_list = filler.get_dates_for_filling()

    if dayz_list:
        await message.answer("Привет! Формирую ведомость")
        builder = ReplyKeyboardBuilder()
        for day in dayz_list:
            builder.add(KeyboardButton(text=day))
        builder.adjust(4)
        await message.answer("Дата?", reply_markup=builder.as_markup(resize_keyboard=True,
                                                                     input_field_placeholder="Выберите дату",
                                                                     ))
    else:
        await message.answer("Привет! Все заполнено!")


@router.message(F.text.func(lambda text: text in filler.days_for_filling))
async def change_a_date(message: Message):
    day_date = filler.days_for_filling[message.text]
    filler.change_the_day_row(day_date)
    await message.reply(f"Принято. Чтоб передать данные, дайте команду /fill",
                        reply_markup=ReplyKeyboardRemove())


router2 = Router()


def get_categories_keyboard(keyboard, cat_list):
    for key in cat_list:
        keyboard.add(KeyboardButton(text=key))
    keyboard.adjust(4)
    return keyboard.as_markup(resize_keyboard=True)


@router2.message(Command("fill"))
async def get_a_cell_keyboard(message: Message):
    if not filler.day_frame.empty:
        filler.get_non_filled_categories()
        if not filler.non_filled_categories:
            await message.reply("Все заполнено!")
            # здесь нужна функция, которая поставит "Y" в ведомость. проверка на чухана (меня)
        else:
            kb = ReplyKeyboardBuilder()
            keyboard = get_categories_keyboard(kb, filler.non_filled_categories)
            await message.answer("Выберите категорию для заполнения", reply_markup=keyboard)
    else:
        await message.reply("Сначала нужно выбрать дату! Дайте команду /start")


def get_filling_inline(inline, cat_data):
    for i in cat_data['keys']:
        inline.add(InlineKeyboardButton(text=str(i), callback_data=f'num_{i}'))
    inline.add(InlineKeyboardButton(text='не мог', callback_data=f'num_{i}'))
    inline.add(InlineKeyboardButton(text='забыл', callback_data=f'num_{i}'))
    # надо красивое тут сдлать!
    inline.adjust(5)
    return inline


@router2.message(F.text.func(lambda text: text in filler.non_filled_categories))
async def change_a_category(message: Message):
    if filler.non_filled_categories:
        cat_name = message.text

        cat_info_ser = filler.get_cell_description(cat_name)
        answer = [i for i in cat_info_ser[['description', 'hint']] if i]
        answer = '\n'.join(answer)
        if answer:
            await message.reply(answer, reply_markup=ReplyKeyboardRemove())
        else:
            ReplyKeyboardRemove()

        if 'keys' in cat_info_ser:
            filler.filled[cat_name] = None
            callback = InlineKeyboardBuilder()
            callback = get_filling_inline(callback, cat_info_ser)
            await message.answer(f"Заполняем {cat_name}", reply_markup=callback.as_markup())
        else:
            await message.answer(f"Не могу заполнить {cat_name}")

        filler.non_filled_categories.remove(message.text)
        time.sleep(3.0)
        # здесь хотелочь бы при наличии отклика на колбэк вернуть новую клаву

        kb = ReplyKeyboardBuilder()
        keyboard = get_categories_keyboard(kb, filler.non_filled_categories)
        await message.answer("Следующая категория?", reply_markup=keyboard)
    else:
        await message.reply('Все заполнено!', reply_markup=ReplyKeyboardRemove())


@router2.callback_query(F.data.contains('num_'))
async def fill_a_cell(callback: CallbackQuery):
    for i in filler.filled:
        if not filler.filled[i]:
            cat_name = i
            cat_value = callback.data.split('_')[1]
            if cat_value == 'не мог':
                cat_value = 'can`t'
            elif cat_value == 'забыл':
                cat_value = '!'
            filler.filled[cat_name] = cat_value

            await callback.answer(f"Вы заполнили {cat_name}")
    print(filler.filled)
