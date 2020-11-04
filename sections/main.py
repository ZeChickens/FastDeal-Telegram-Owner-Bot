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
        text = self._form_text_main_manu(chat_id)
        markup = self._create_markup_main_menu()
            
        if chat_id is not None:
            self.bot.send_message(chat_id, text=text, reply_markup=markup)
        else:
            self.send_message(call, text=text, reply_markup=markup)

    def _create_markup_main_menu(self):
        markup = InlineKeyboardMarkup()

        # Account button
        account_btn_text = self.data.message.button_account_cabinet
        account_btn_callback = self.form_account_callback(action="Cabinet", prev_msg_action="Edit")
        account_btn = InlineKeyboardButton(text=account_btn_text, callback_data=account_btn_callback)
        markup.add(account_btn)

        return markup


    def _form_text_main_manu(self, chat_id):
        text = self.data.message.start_registered_false

        return text