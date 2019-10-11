import sys

import cherrypy
import telebot
from telebot import types

import config
from cards_dao import CardsDao

bot = telebot.TeleBot(config.token)
dao = CardsDao(sys.argv[1])

last_id = None

WEBHOOK_HOST = '63.34.10.164'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % config.token


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


@bot.message_handler(commands=['random'])
def random_command(message):
    get_random_question(message)


@bot.message_handler(func=lambda message: message.text == 'Get random question')
def get_random_question(message):
    card_id, front = dao.get_random_question()
    global last_id
    last_id = card_id
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton('Check answer'))
    bot.send_message(message.chat.id, str(front), reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Check answer')
def handle_message(message):
    markup = get_random_question_markup()
    if last_id is not None:
        back = dao.get_card_back_by_id(last_id)
        bot.send_message(message.chat.id, str(back), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Send /random to get random question.', reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, 'Send /random or press the button above to get random question.',
                     reply_markup=get_random_question_markup())


def get_random_question_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton('Get random question'))
    return markup


bot.remove_webhook()
# bot.polling()


bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
