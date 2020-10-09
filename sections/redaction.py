from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section

class Redaction(Section):

    def __init__(self, data, order):
        super().__init__(data=data)
        self.order = order

        self.REDACTION_CHAT_ID = self.data.REDACTION_CHAT_ID#-1001153596317

    def process_callback(self, call):
        #Redaction;{action};{order_id}
        action, order_id = call.data.split(";")[1:3]

        if action == "CheckOrder":
            message = call.message
            self.send_order_check( message, order_id=order_id)

        elif action == "Description":
            self.send_order_description(call, order_id=order_id)

        elif action == "Confirm":
            self.confirm_order(call, order_id=order_id)

        elif action == "Reject":
            self.reject_order(call, order_id=order_id)

        elif action == "CloseOrder":
            order_id = int(call.data.split(";")[2])
            self.close_order(call=call, order_id=order_id)
        
        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def process_text(self, message):
        text = message.text

        if "CONFIRMED" in text:
            order_id = int(text.split("_")[1].split("@")[0])
            self.send_new_order_to_owner(order_id)

    def send_new_order_to_owner(self, order_id):
        #To redaction
        redaction_text = self.data.message.redaction_order_sent_to_owner
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=redaction_text)

        #To owner
        order = self.data.get_order(where={"OrderID":order_id})[0]
        channel = self.data.get_channel(where={"ChannelID":order.ChannelID})[0]
        owner = self.data.get_owner(where={"OwnerID":channel.OwnerID})[0]
        self.data.update_order(set_={"Status":1}, where={"OrderID":order_id})
        
        owner_chat_id = owner.ChatID
        self.order.send_order_status_notification(chat_id=owner_chat_id, order_id=order_id)

    def send_order_check(self, message, order_id):
        self.data.update_order(set_={"Status":2}, where={"OrderID":order_id})

        owner_chat_id = message.chat.id
        message_id = message.message_id
        
        #in redaction
        self.order.send_order_status_notification(chat_id=self.REDACTION_CHAT_ID, order_id=order_id)

        #in owner
        text_to_owner = self.data.message.order_sent_to_redaction_check
        self.bot.edit_message_text(chat_id=owner_chat_id, message_id=message_id, text=text_to_owner, reply_markup=None, parse_mode="HTML")

    def send_order_description(self, call, order_id):
        chat_id = self.REDACTION_CHAT_ID
        self.bot.delete_message(chat_id, call.message.message_id)

        text, photo = self.order.form_order_description(order_id=order_id)
        markup = InlineKeyboardMarkup()
        
        confirm_button_text = "✅"
        confirm_button_callback = self.form_redaction_callback(action="Confirm", order_id=order_id)
        confirm_button = InlineKeyboardButton(text=confirm_button_text, callback_data=confirm_button_callback)

        reject_button_text = "❌"
        reject_button_callback = self.form_redaction_callback(action="Reject", order_id=order_id)
        reject_button = InlineKeyboardButton(text=reject_button_text, callback_data=reject_button_callback)
        
        markup.add(confirm_button, reject_button)

        try:
            self.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=markup, parse_mode="HTML")
        except:
            self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode="HTML")

    def confirm_order(self, call, order_id):
        self.bot.edit_message_reply_markup(chat_id=self.REDACTION_CHAT_ID, message_id=call.message.message_id, reply_markup=None)
        
        #get all data from database
        order = self.data.get_order(where={"OrderID":order_id})[0]
        channel = self.data.get_channel(where={"ChannelID":order.ChannelID})[0]
        owner = self.data.get_owner(where={"OwnerID":channel.OwnerID})[0]

        #chat id
        owner_chat_id = owner.ChatID

        #update order status
        self.data.update_order(set_={"Status":3}, where={"OrderID":order.OrderID})

        #redaction
        notify_another_bot_text = self.data.message.redaction_finished_order(order_id)
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=notify_another_bot_text)

        #owner
        self.order.send_order_status_notification(chat_id=owner_chat_id, order_id=order_id)

    def reject_order(self, call, order_id):
        self.bot.edit_message_reply_markup(chat_id=self.REDACTION_CHAT_ID, message_id=call.message.message_id, reply_markup=None)

        #get all data from database
        order = self.data.get_order(where={"OrderID":order_id})[0]
        channel = self.data.get_channel(where={"ChannelID":order.ChannelID})[0]
        owner = self.data.get_owner(where={"OwnerID":channel.OwnerID})[0]

        #chat id
        owner_chat_id = owner.ChatID

        #redaction
        input_reject_reason_text = self.data.message.redaction_reject_reason
        message = self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=input_reject_reason_text)

        #next step
        self.bot.register_next_step_handler(message, self.complete_rejection, owner_chat_id=owner_chat_id, order_id=order_id)
    
    def complete_rejection(self, message, **kwargs):
        owner_chat_id = kwargs["owner_chat_id"]
        order_id = kwargs["order_id"]

        redaction_comment = message.text

        self.data.update_order(set_={"RedactionComment":redaction_comment}, where={"OrderId":order_id})
        self.data.update_order(set_={"Status":1}, where={"OrderId":order_id})

        #redaction
        order_rejected_text = self.data.message.redaction_order_completion_rejected
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=order_rejected_text)

        #owner
        self.order.send_order_status_notification(chat_id=owner_chat_id, order_id=order_id)

    #close order which is declined by owner
    def close_order(self, call, order_id):
        owner_chat_id = call.message.chat.id
        message_id = call.message.message_id

        self.bot.delete_message(chat_id=owner_chat_id, message_id=message_id)

        #update order
        rejection_reason_index = int(call.data.split(";")[3])
        rejection_reason = self.data.message.button_owner_reject_reasons[rejection_reason_index]
        self.data.update_order(set_={"Status":-2, "OwnerComment":rejection_reason}, where={"OrderID":order_id})

        #send trigger to another bot
        trigger_text = self.data.message.redaction_finished_order(order_id=order_id)
        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=trigger_text)

        #send notification to redaction
        self.order.send_order_status_notification(chat_id=self.REDACTION_CHAT_ID, order_id=order_id)

        #send massage to owner
        text = self.data.message.button_owner_order_rejected
        self.bot.send_message(chat_id=owner_chat_id, text=text)

    def command_in_group_error(self):
        text = self.data.message.redaction_command_error

        self.bot.send_message(chat_id=self.REDACTION_CHAT_ID, text=text)