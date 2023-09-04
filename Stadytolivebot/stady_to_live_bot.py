import telebot
from telebot import types
from My_token import TOKEN


DAYZ = ['1.09.2013', '2.09.2023']

bot = telebot.TeleBot(TOKEN)

name = None
username = None
descriptions = {1: 'прыг_скок', 2: 'сядь на голову', 3: 'чигарики-чок-чигары'}
variants = {1: ['1', '2'], 2: ['сясь'], 3: ['комарики', 'мухи', 'комары']}
container = {1: '', 2: '', 3: ''}


@bot.message_handler(commands=['start'])
def start_message(message):
    global name, username
    name = message.from_user.first_name
    username = message.from_user.username
    bot.send_message(message.chat.id, 'Привет. Это бот для заполнения таблицы. Выберите число для заполнения')


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    change_a_date(message)
    container['date'] = message
    for q in descriptions:
        answer_a_question(message, q)


def change_a_date(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in DAYZ:
        b = types.KeyboardButton(i)
        markup.add(b)
    bot.send_message(message.chat.id, 'Выбери дату из списка', reply_markup=markup)
    container['date'] = message.text


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
