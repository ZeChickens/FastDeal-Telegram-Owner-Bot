from telebot import TeleBot

from data import Data
from system import System
from client import Client

from sections.main import Main
from sections.channel import Channel
from sections.order import Order
from sections.redaction import Redaction

import logging
from time import sleep

import error_logging

API_TOKEN = "719905869:AAFPbJzaoDLu42mzSeSX95DG6SjoHrPdCu8"

bot = TeleBot(API_TOKEN)
data = Data(bot=bot)
system = System(data=data)

client = Client(data=data)
main_menu = Main(data=data)
order = Order(data=data, client=client)
channel = Channel(data=data, client=client)
redaction = Redaction(data=data, order=order)

@bot.message_handler(commands=['start'])
def start_bot(message):
    if message.chat.id == data.REDACTION_CHAT_ID:
        redaction.command_in_group_error()
        return
    system.clear(chat_id=message.chat.id)
    system.add_client(message)
    main_menu.send_start_message(message)

    system.update_client_interaction_time(message)


@bot.message_handler(commands=['orders'])
def orders_list(message):
    system.clear(chat_id=message.chat.id)
    system.update_client_interaction_time(message)

    try:
        order.send_order_list(message=message)
    except:
        print("Exception in orders")

@bot.message_handler(commands=['my_channels'])
def channels_list(message):
    system.clear(chat_id=message.chat.id)
    system.update_client_interaction_time(message)

    try:
        channel.send_channel_list(chat_id=message.chat.id)
    except:
        print("Exception in my_channels")

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
    logger = logging.Logger("Polling")
    while True:
        try:
            bot.infinity_polling(none_stop=True)
        except Exception as e:
            logger.error(e)

            sleep(15)

            logging.info("Running again!")