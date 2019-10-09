from telebot import types
import config
import telebot

from cards_dao import CardsDao

bot = telebot.TeleBot(config.token)
dao = CardsDao('cards.db')

last_id = None


@bot.message_handler(commands=['random'])
def get_random_question(message):
    card_id, front = dao.get_random_question()
    global last_id
    last_id = card_id
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton('Check answer'))
    bot.send_message(message.chat.id, str(front), reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Check answer')
def handle_message(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    if last_id is not None:
        back = dao.get_card_back_by_id(last_id)
        bot.send_message(message.chat.id, str(back), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Send /random to get random question.', reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, 'Send /random to get random question.', reply_markup=markup)


bot.polling()
