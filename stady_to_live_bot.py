import telebot
from telebot import types
from My_token import TOKEN
import vedomost_filler as vfill
# https://habr.com/ru/articles/580408/

month = 'sep23'
path = f'months/{month}/{month}.xlsx'

filler = vfill.VedomostFiller(path, 'Lera')
days_for_filling = filler.get_dates_for_filling()
# нужно по другому представить дату, типа для понятливого чтения, нужно так же ее тудым сюдым конвертить

bot = telebot.TeleBot(TOKEN)

name = None
username = None


@bot.message_handler(commands=['start'])
def start_message(message):
    global name, username
    name = message.from_user.first_name
    username = message.from_user.username
    bot.send_message(message.chat.id, 'Привет!')


@bot.message_handler(commands=['button'])
def change_a_date(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in days_for_filling:
        b = types.KeyboardButton(i)
        markup.add(b)
    bot.send_message(message.chat.id, 'Выбери дату из списка', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def message_reply(message):
    if message.text in days_for_filling:
        bot.send_message(message.chat.id, f'заполняем {message}')
        filler.fill_the_day_row(message.text)


#def get_text_message(message):
#    change_a_date(message)
#    container['date'] = message
#    for q in descriptions:
#        answer_a_question(message, q)
#
#


def answer_a_question(message, q):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    answers = variants[q]
    for a in answers:
        b = types.KeyboardButton(a)
        markup.add(b)
    bot.send_message(message.chat.id, text=descriptions[q])
    container[q] = message.text


bot.polling()
print(container)
