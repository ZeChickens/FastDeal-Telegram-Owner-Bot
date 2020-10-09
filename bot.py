from telebot import TeleBot, logger
from telebot.types import Update

from data import Data
from system import System
from client import Client

from sections.main import Main
from sections.channel import Channel
from sections.order import Order
from sections.redaction import Redaction

import logging
import flask
from time import sleep

import error_logging

API_TOKEN = "719905869:AAFPbJzaoDLu42mzSeSX95DG6SjoHrPdCu8"

WEBHOOK_HOST = '34.123.227.101'  # external ip in Computer engine
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './url_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './url_private.key'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

logger.setLevel(logging.INFO)

bot = TeleBot(API_TOKEN)
data = Data(bot=bot)
system = System(data=data)

client = Client(data=data)
main_menu = Main(data=data)
order = Order(data=data, client=client)
channel = Channel(data=data, client=client)
redaction = Redaction(data=data, order=order)

app = flask.Flask(__name__)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(commands=['start'])
def start_bot(message):
    if message.chat.id == data.REDACTION_CHAT_ID:
        redaction.command_in_group_error()
        return
    system.clear(chat_id=message.chat.id)
    system.add_client(message)
    main_menu.send_start_message(chat_id=message.chat.id)

    system.update_client_interaction_time(message)

@bot.message_handler(commands=['orders'])
def orders_list(message):
    chat_id=message.chat.id

    system.clear(chat_id=message.chat.id)
    system.update_client_interaction_time(message)

    try:
        order.send_order_list(chat_id=chat_id)
    except:
        print("Exception in orders")

@bot.message_handler(commands=['my_channels'])
def channels_list(message):
    chat_id = message.chat.id

    system.clear(chat_id=message.chat.id)
    system.update_client_interaction_time(message)

    try:
        channel.send_channel_list(chat_id=chat_id)
    except:
        print("Exception in my_channels")

@bot.callback_query_handler(func=lambda call: "Main" in call.data.split(";")[0])
def handle_main_menu_query(call):
    system.clear(chat_id=call.message.chat.id)
    system.update_client_interaction_time(call.message)

    try:
        main_menu.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.callback_query_handler(func=lambda call: "Order" in call.data.split(";")[0])
def handle_order_query(call):
    system.clear(chat_id=call.message.chat.id)
    system.update_client_interaction_time(call.message)

    try:
        order.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.callback_query_handler(func=lambda call: "Redaction" in call.data)
def redaction_decision(call):
    system.clear(chat_id=call.message.chat.id)
    system.update_client_interaction_time(call.message)

    try:
        redaction.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.callback_query_handler(func=lambda call: "Channel" in call.data.split(";")[0])
def handle_channel_query(call):
    system.clear(chat_id=call.message.chat.id)
    system.update_client_interaction_time(call.message)
    
    try:
        channel.process_callback(call)
    except:
        oops(call, current_frame=error_logging.currentframe())

@bot.message_handler(func=lambda message: message.chat.id == data.REDACTION_CHAT_ID)
def redaction_message_handler(message):
    redaction.process_text(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_etc_query(call):
    
    if call.data == "DELETE":
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            bot.answer_callback_query(call.id, text=data.message.delete_error)
    elif call.data == "IGNORE":
        bot.answer_callback_query(call.id)
    else:
        oops(call, current_frame=error_logging.currentframe())

def oops(call, current_frame, additional_info=None):
    oops_text = data.message.oops
    bot.answer_callback_query(call.id, text=oops_text)

    if additional_info is None:
        additional_info = call.data

    error_logging.send_error_info_message(bot, current_frame, additional_info=additional_info)

if __name__ == "__main__":
    order.start_notifications()
    bot.remove_webhook()

    sleep(1)
    # Set webhook
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    # Start flask server
    app.run(host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
            debug=True)
            debug=True)
