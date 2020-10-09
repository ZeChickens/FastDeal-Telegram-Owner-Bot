from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

class Main(Section):
    def __init__(self, data):
        super().__init__(data=data)

    def process_callback(self, call):
        action = call.data.split(";")[1]

        if action == "Start":
            self.send_start_message(call=call)
            
        elif action == "Special":
            self.in_development(call)

        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_start_message(self, chat_id=None, call=None):
        """Send start message with introduction to bot.\n
        Specify chat_id if it called through command, otherwise
        specify call if it called after button pressed.
        """
        text = self.data.message.start_registered_false
        markup = InlineKeyboardMarkup()

        # Channels button
        channels_btn_text = self.data.message.button_channel_my
        channels_btn_callback = self.form_channel_callback(action="List", prev_msg_action="Edit")
        channels_btn = InlineKeyboardButton(text=channels_btn_text, callback_data=channels_btn_callback)
        markup.add(channels_btn)     

        # Orders button
        orders_btn_text = self.data.message.button_order_my
        orders_btn_callback = self.form_order_callback(action="List", order_id=None, prev_msg_action="Edit")
        orders_btn = InlineKeyboardButton(text=orders_btn_text, callback_data=orders_btn_callback)
        markup.add(orders_btn)       

        # Add Channel button
        #channel_add_btn_text = self.data.message.button_channel_add_new
        #channel_add_btn_callback = "Channel;Add;None"
        #channel_add_btn = InlineKeyboardButton(text=channel_add_btn_text, callback_data=channel_add_btn_callback)
        #markup.add(channel_add_btn)
            
        if chat_id is not None:
            self.bot.send_message(chat_id, text=text, reply_markup=markup)
        else:
            self.send_message(call, text=text, reply_markup=markup)
