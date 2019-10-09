import telebot

bot = telebot.TeleBot("941766205:AAEDy7VwM4yd0Gb6Dyg-SN5PyOLq7u1y2F4")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")
