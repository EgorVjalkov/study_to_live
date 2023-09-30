import pandas as pd
import vedomost_filler as vfill
from datetime import datetime

from My_token import TOKEN
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters import CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder


logging.basicConfig(level=logging.INFO)


class FillerBot:
    def __init__(self, path_to_vedomost, user_dict):
        self.bot = Bot(TOKEN)
        self.dp = Dispatcher()

        self.filler_prog = vfill.VedomostFiller(path_to_vedomost)
        self.user_name_dict = user_dict

        self.days_for_filling = {}

        self.default_day_frame = pd.DataFrame()

        self.cell = ''

    @property
    def day_frame(self):
        return self.default_day_frame

    @day_frame.setter
    def day_frame(self, day_frame):
        self.default_day_frame = day_frame


month = 'sep23'
path = f'months/{month}/{month}.xlsx'
username_dict = {'Jegor': 'Egr'}

filler_bot = FillerBot(path, username_dict)


@filler_bot.dp.message(Command("start"))
async def cmd_start_and_get_r_vedomost(message: types.Message):
    name = message.from_user.first_name
    filler_bot.filler_prog.r_name = filler_bot.user_name_dict[name]
    filler_bot.filler_prog.get_r_vedomost()
    dayz_list = filler_bot.filler_prog.get_dates_for_filling()

    if dayz_list:
        await message.answer("Привет! Формирую ведомость")
        builder = ReplyKeyboardBuilder()
        for day in dayz_list:
            builder.add(types.KeyboardButton(text=day))
        builder.adjust(4)
        await message.answer("Дата?", reply_markup=builder.as_markup(resize_keyboard=True,
                                                                     input_field_placeholder="Выберите дату",
                                                                     ))
    else:
        await message.answer("Привет! Все заполнено!")


async def get_a_cell_keyboard(message: types.Message):
    if not filler_bot.day_frame.empty:
        # почемуто не работает комада /fill
        # нужно сделать клаву в области интересов филлер бота. так можно будет исключать из нее кнопки
        builder = ReplyKeyboardBuilder()
        for cell in filler_bot.day_frame.columns:
            builder.add(types.KeyboardButton(text=cell))
        builder.adjust(4)
        await message.answer("Выберите категорию для заполнения",
                             reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        await message.reply("Сначала нужно выбрать дату!")


@filler_bot.dp.message(F.text)
async def change_a_date(message: types.Message):
    if message.text in filler_bot.filler_prog.days_for_filling:
        filler_bot.day_frame = filler_bot.filler_prog.change_the_day_row(
            filler_bot.filler_prog.days_for_filling[message.text])
        await message.reply(f"Принято. Чтоб передать данные, дайте команду /fill",
                            reply_markup=types.ReplyKeyboardRemove())




@filler_bot.dp.message(F.text)
async def fill_a_cell(message: types.Message):
    if not filler_bot.day_frame.empty:
        if message.text in filler_bot.day_frame.columns:
            pass


async def main():
    await filler_bot.dp.start_polling(filler_bot.bot)
    filler_bot.dp.message.register(get_a_cell_keyboard, Command("fill"))


if __name__ == '__main__':
    asyncio.run(main())


#@filler_bot.bot.message_handler(commands=['start'], content_types=['text'])
#def start_and_change_a_date(message):
#    r_name = filler_bot.user_name_dict[message.from_user.first_name]
#    filler_bot.filler_prog.r_name = r_name
#    filler_bot.filler_prog.get_r_vedomost()
#    filler_bot.days_for_filling = filler_bot.filler_prog.get_dates_for_filling()
#
#    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#    for i in filler_bot.days_for_filling:
#        b = types.KeyboardButton(i)
#        markup.add(b)
#    filler_bot.bot.send_message(message.chat.id, , reply_markup=markup)
#    while True:
#        if message.text in filler_bot.days_for_filling:
#            filler_bot.day_frame = filler_bot.days_for_filling[message.text]
#            for cell in filler_bot.day_frame.columns:
#                print(cell)
#                mark = filler_bot.day_frame[cell].to_list()[0]
#                row_index = filler_bot.day_frame.index[0]
#                if pd.isna(mark):
#                    cell_description = filler_bot.filler_prog.get_cell_description(cell)
#                    descr_message = cell_description['description']
#                    hint_message = cell_description['hint']
#                    filler_bot.bot.send_message(message.chat.id, descr_message)
#                    if hint_message:
#                        filler_bot.bot.send_message(message.chat.id, hint_message)
#
#
#def change_by_message(message, variants_dict):
#    answer = message.text
#    if answer in variants_dict:
#        filler_bot.bot.send_message(message.chat.id, f'Вы выбрали {answer}')
#        return variants_dict[answer]
#
#        #print(cat_description['description'])
#        #if cat_description['hint']:
#        #    print(cat_description['hint'])
#        #print()
#        # здесь пока только тип заполняемого, именно тут интегрируется бот с его кнопками и т.д.
#        #filler_bot.day_frame.loc[row_index, cell] = cell_description['type']
#        # сделать нужно филлерчек
#
#
#filler_bot.bot.polling()
