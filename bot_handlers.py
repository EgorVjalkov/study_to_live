from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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


@router2.message(F.text.func(lambda text: text in filler.non_filled_categories))
async def change_a_category(message: Message):
    if filler.non_filled_categories:
        cat_info_dict = filler.get_cell_description(message.text)
        if cat_info_dict['hint']:
            answer = f'{cat_info_dict["description"]}\n{cat_info_dict["hint"]}'
        else:
            answer = f'{cat_info_dict["description"]}'
        await message.reply(answer, reply_markup=ReplyKeyboardRemove())

        filler.non_filled_categories.remove(message.text)

        kb = ReplyKeyboardBuilder()
        keyboard = get_categories_keyboard(kb, filler.non_filled_categories)
        await message.answer("Следующая категория?", reply_markup=keyboard)
    else:
        await message.reply('Все заполнено!', reply_markup=ReplyKeyboardRemove())



