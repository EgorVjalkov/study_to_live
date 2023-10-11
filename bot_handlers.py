from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot_main import filler, username_dict


router = Router()
# надо потестироваь на предмет асинхронности, почитать всякое про асунх
# запуск filler должен быть асинхронным!!!!
# подумай как очистить все поля и заново перезапустить филлер
# доделай с solid категориями


@router.message(Command("start"))
async def cmd_start_and_get_r_vedomost(message: Message):
    filler.restart()
    filler.r_name = username_dict[message.from_user.first_name]
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
    keyboard.add(KeyboardButton(text='завершить заполнение'))
    keyboard.adjust(4)
    return keyboard.as_markup(resize_keyboard=True)


@router2.message(Command("fill"))
# и тут вилка. с акттивацией команды /fill начинает заново все заполнять
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
    if 'keys' in cat_data:
        keys = [InlineKeyboardButton(text=str(i), callback_data=f'fill_{i}') for i in cat_data['keys']]
        inline.row(*keys)
    inline.row(InlineKeyboardButton(text='не мог', callback_data='fill_не мог'),
               InlineKeyboardButton(text='забыл', callback_data='fill_забыл'))
    # надо красивое тут сдлать!
    return inline


@router2.message(F.text.func(lambda text: text in filler.non_filled_categories))
async def change_a_category(message: Message):
    # как убрать клаву без сообщения???? можно размутиться с удалением сообщения
    # https://ru.stackoverflow.com/questions/1497723/%D0%9A%D0%B0%D0%BA-%D1%83%D0%B1%D1%80%D0%B0%D1%82%D1%8C-%D0%BA%D0%BB%D0%B0%D0%B2%D0%B8%D0%B0%D1%82%D1%83%D1%80%D1%83-%D0%B1%D0%BE%D1%82%D0%B0-aiogram
    if filler.non_filled_categories:
        cat_name = message.text

        cat_info_ser = filler.get_cell_description(cat_name)
        answer = [i for i in cat_info_ser[['description', 'hint']] if i]
        if 'time' in cat_info_ser['type']:
            answer.append("Напишите сообщение в формате: чч:мм или нaжмите кнопку на экране")

        answer = '\n'.join(answer)
        if not answer:
            answer = 'Нажмите кнопку на экране'

        callback = InlineKeyboardBuilder()
        callback = get_filling_inline(callback, cat_info_ser)
        await message.answer(answer, reply_markup=callback.as_markup())

        filler.filled[cat_name] = None
        filler.non_filled_categories.remove(message.text)

        kb = ReplyKeyboardBuilder()
        keyboard = get_categories_keyboard(kb, filler.non_filled_categories)

        #здесь хотелочь бы при наличии отклика на колбэк вернуть новую клаву Надо мутить с асинхронью
        await message.answer("Следующая категория?", reply_markup=keyboard)
    else:
        await message.reply('Все заполнено!', reply_markup=ReplyKeyboardRemove())


@router2.message(F.text == 'завершить заполнение')
async def abort_filling_by_message(message: Message):
    filled_in_str = ', '.join(list(filler.filled.keys()))
    if filled_in_str:
        answer = f'Вы заполнили {filled_in_str}'
    else:
        answer = 'Вы ничего не заполнили'

    filler.save_day_data()
    await message.answer(f'Завершeно! {answer}', reply_markup=ReplyKeyboardRemove())


router3 = Router()


@router3.callback_query(F.data.contains('fill_'))
async def fill_a_cell(callback: CallbackQuery):
    cat_value = callback.data.split('_')[1]
    filled_cat = filler.fill_a_cell(cat_value)
    print(filler.filled)
    if filler.is_day_filled():
        filler.save_day_data()
    await callback.answer(f"Вы заполнили {filled_cat}")


@router3.message(F.text.func(lambda text: ':' in text))
async def fill_a_cell_with_time(message: Message):
    filled_cat = filler.fill_a_cell(message.text)
    print(filler.filled)
    if filled_cat:
        if filler.is_day_filled():
            filler.save_day_data()
        await message.answer(f"Вы заполнили {filled_cat}")

