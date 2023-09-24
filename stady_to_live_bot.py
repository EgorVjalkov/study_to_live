import pandas as pd
from My_token import TOKEN
import vedomost_filler as vfill
# https://habr.com/ru/articles/580408/
# не понимаю почему не доходит до необходимого, замуть какаято с хэндлерами


class FillerBot:
    def __init__(self, path_to_vedomost, user_dict):
        self.bot = telebot.TeleBot(TOKEN)
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


@filler_bot.bot.message_handler(commands=['start'], content_types=['text'])
def start_and_change_a_date(message):
    r_name = filler_bot.user_name_dict[message.from_user.first_name]
    filler_bot.filler_prog.r_name = r_name
    filler_bot.filler_prog.get_r_vedomost()
    filler_bot.days_for_filling = filler_bot.filler_prog.get_dates_for_filling()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in filler_bot.days_for_filling:
        b = types.KeyboardButton(i)
        markup.add(b)
    filler_bot.bot.send_message(message.chat.id, 'Превет! Выбери дату из списка', reply_markup=markup)
    while True:
        if message.text in filler_bot.days_for_filling:
            filler_bot.day_frame = filler_bot.days_for_filling[message.text]
            for cell in filler_bot.day_frame.columns:
                print(cell)
                mark = filler_bot.day_frame[cell].to_list()[0]
                row_index = filler_bot.day_frame.index[0]
                if pd.isna(mark):
                    cell_description = filler_bot.filler_prog.get_cell_description(cell)
                    descr_message = cell_description['description']
                    hint_message = cell_description['hint']
                    filler_bot.bot.send_message(message.chat.id, descr_message)
                    if hint_message:
                        filler_bot.bot.send_message(message.chat.id, hint_message)


def change_by_message(message, variants_dict):
    answer = message.text
    if answer in variants_dict:
        filler_bot.bot.send_message(message.chat.id, f'Вы выбрали {answer}')
        return variants_dict[answer]

        #print(cat_description['description'])
        #if cat_description['hint']:
        #    print(cat_description['hint'])
        #print()
        # здесь пока только тип заполняемого, именно тут интегрируется бот с его кнопками и т.д.
        #filler_bot.day_frame.loc[row_index, cell] = cell_description['type']
        # сделать нужно филлерчек


filler_bot.bot.polling()
