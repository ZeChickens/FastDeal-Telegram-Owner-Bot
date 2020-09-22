from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

class Main(Section):
    def __init__(self, data):
        super().__init__(data=data)

    def send_start_message(self, message):
        owner_chat_id = message.chat.id
        owner = self.data.get_owner(where={"ChatID":owner_chat_id})[0]

        is_registered = len(self.data.get_channel(where={"OwnerID":owner.OwnerID})) > 0

        if is_registered:
            #кількість очікуваних замовлень
            text = self.data.message.start_registered_true
        else:
            text = self.data.message.start_registered_false

        markup = InlineKeyboardMarkup()
        channel_add_btn_text = self.data.message.button_channel_add_new
        channel_add_btn_callback = "Channel;Add;None"
        channel_add_btn = InlineKeyboardButton(text=channel_add_btn_text, callback_data=channel_add_btn_callback)
        markup.add(channel_add_btn)
            
        self.bot.send_message(chat_id=owner_chat_id, text=text, reply_markup=markup, parse_mode="HTML")
