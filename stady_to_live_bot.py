import pandas as pd
import vedomost_filler as vfill
from datetime import datetime

from My_token import TOKEN
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters import CommandObject


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
    await message.answer("Привет! Формирую ведомость")

    dayz_list = filler_bot.filler_prog.get_dates_for_filling()
    dayz_kb = [types.KeyboardButton(text=i) for i in dayz_list]
    dayz_kb = [dayz_kb]
        
    keyboard = types.ReplyKeyboardMarkup(keyboard=dayz_kb,
                                         resize_keyboard=True,
                                         input_field_placeholder='Выберите дату')
    await message.answer("Дата?", reply_markup=keyboard)


async def cmd_t1(message: types.Message):
    await message.reply("тест1")


async def cmd_t2(message: types.Message):
    await message.reply("теcт2")


@filler_bot.dp.message(Command("name"))
async def cmd_name(message: types.Message, command: CommandObject):
    list_ = [1, 2]
    if command.args:
        list_.append(command.args)
        await message.reply(f'{list_}')
    else:
        await message.answer("укажи имя по сле команды /name")


async def main():
    filler_bot.dp.message.register(cmd_t1, Command("test1"))
    filler_bot.dp.message.register(cmd_t2, Command("test2"))
    await filler_bot.dp.start_polling(filler_bot.bot)


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
