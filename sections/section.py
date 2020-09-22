from telebot.types import InlineKeyboardButton

class Section:

    def __init__(self, data):
        self.data = data
        self.bot = self.data.bot

    def process_callback(self, call):
        pass

    def form_main_callback(self, action):
        return f"Main;{action}"

    def form_channel_callback(self, action, channel_id=None, tag_id=0):
        return f"Channel;{action};{channel_id};{tag_id}"

    def form_order_callback(self, action, order_id, prev_msg_action=None):
        return f"Order;{action};{order_id};{prev_msg_action}"

    def form_redaction_callback(self, action, order_id, reserved=None):
        return f"Redaction;{action};{order_id};{reserved}"

    def create_delete_button(self):
        return InlineKeyboardButton(text="❌", callback_data="DELETE")

    def oops(self, call):
        oops_text = self.data.message.oops
        self.bot.answer_callback_query(call.id, text=oops_text)