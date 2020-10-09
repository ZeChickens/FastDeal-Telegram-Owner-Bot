from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, date
from threading import Thread
from time import sleep

from sections.section import Section

class Order(Section):

    notification_hour = 10

    def __init__(self, data, client):
        super().__init__(data=data)
        self.client = client

    def process_callback(self, call):
        #Order;{action};{order_id}
        action, order_id = call.data.split(";")[1:3]
        
        if action == "Confirm":
            self.send_confirmation(call=call, order_id=order_id, completion=True)

        elif action == "List":
            self.send_order_list(call=call)
        
        elif action == "ConfirmationInstruction":
            self.send_confirmation_instruction(call=call, order_id=order_id)

        elif action == "Reject":
            self.send_confirmation(call=call, order_id=order_id, rejection=True)

        elif action == "RejectReason":
            self.send_reject_reason(call=call, order_id=order_id)

        elif action == "Description":
            self.send_order_description(call=call, order_id=order_id)

        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def start_notifications(self):
        """
        Starts new thread to notify owners about theirs uncompleted orders
        """
        order_notifications_thread = Thread(target=self.send_notifications, name="OrderNotifications")
        order_notifications_thread.start()

    def send_notifications(self):
        """
        Sends notifications to owners every day in specific time
        """
        sleep(5)
        while True:
            if datetime.now().hour == self.notification_hour:
                orders = self.data.get_multiple_tables(tables=["Owner", "Channel", "Order"],
                                                       join_type="Right",
                                                       where={"[Order].Status":1})

                for order in orders:
                    order.PostDate = datetime.strptime(order.PostDate, "%Y-%m-%d").date()

                valid_orders = filter(lambda order: order.PostDate >= date.today(), orders)
                expired_orders = filter(lambda order: order.PostDate < date.today(), orders)

                # send notifications about ramaining time
                for valid_order in valid_orders:
                    message_to_owner = self.form_notification_message(post_date=valid_order.PostDate)
                    self.send_order_status_notification(chat_id=valid_order.ChatID, 
                                                        order_id=valid_order.OrderID, text=message_to_owner)
                    sleep(1)
                
                # send notifications about expired time
                # and update orders' status
                for expired_order in expired_orders:
                    message_to_owner = self.form_notification_message(post_date=expired_order.PostDate, expired=True)

                    self.data.update_order(set_={"Status":-3}, where={"OrderID":expired_order.OrderID})
                    self.send_order_status_notification(chat_id=expired_order.ChatID, 
                                                        order_id=expired_order.OrderID, text=message_to_owner)
                    # send notification to redaction
                    self.send_order_status_notification(chat_id=self.data.REDACTION_CHAT_ID,
                                                        order_id=expired_order.OrderID)
                    sleep(1)

                sleep(60 * 60 * 24) # wait 1 day for next notifications
            else:
                sleep(60 * 30) # wait 30 minutes for right time

    def send_order_list(self, chat_id=None, call=None): 
        """Send order list. If called from redaction - send all orders\n
        Specify chat_id if it called through command, otherwise
        specify call if it called after button pressed.
        """     
        if call is not None:
            chat_id = call.message.chat.id
        
        if chat_id == self.data.REDACTION_CHAT_ID:
            return
        else:
            owner = self.data.get_owner(where={"ChatID":chat_id})[0]#
            orders_list = self.get_all_orders(owner=owner)

        markup = InlineKeyboardMarkup()
        for element in orders_list:
            for order in element:
                button = self.create_order_description_button(order=order)
                markup.add(button)

        # if list is called from main menu than send "Back" button
        if call is not None:
            back_button_callback = self.form_main_callback(action="Start", prev_msg_action="Edit")
            back_button = self.create_back_button(callback_data=back_button_callback)
            markup.add(back_button)
        else:
            markup.add(self.create_delete_button())


        text = self.data.message.order_list
        if call is None:
            self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        else:
            self.send_message(call=call, text=text, reply_markup=markup)

    def send_order_description(self, call, order_id):
        chat_id = call.message.chat.id
        
        order = self.data.get_order(where={"OrderID":order_id})[0]
        text, photo = self.form_order_description(order=order)

        markup = InlineKeyboardMarkup()
        #If order is waiting for completion
        if order.Status == 1:
            button_confirm_text = "✅"
            button_confirm_callback = self.form_order_callback(action="Confirm", order_id=order_id)
            button_confirm = InlineKeyboardButton(text=button_confirm_text, callback_data=button_confirm_callback)

            button_reject_text = "❌"
            button_reject_callback = self.form_order_callback(action="Reject", order_id=order_id)
            button_reject = InlineKeyboardButton(text=button_reject_text, callback_data=button_reject_callback)

            markup.add(button_confirm, button_reject)
        #If order is completed and waiting for confirmation
        elif order.Status == 2 and chat_id == self.data.REDACTION_CHAT_ID:
            button_confirm_text = "✅"
            button_confirm_callback = self.form_redaction_callback(action="Confirm", order_id=order_id)
            button_confirm = InlineKeyboardButton(text=button_confirm_text, callback_data=button_confirm_callback)

            button_reject_text = "❌"
            button_reject_callback = self.form_redaction_callback(action="Reject", order_id=order_id)
            button_reject = InlineKeyboardButton(text=button_reject_text, callback_data=button_reject_callback)

            markup.add(button_confirm, button_reject)
        else:
            # Back button
            if chat_id != self.data.REDACTION_CHAT_ID:
                back_button_callback = self.form_order_callback(action="List", order_id=None, prev_msg_action="Delete")
                back_button = self.create_back_button(callback_data=back_button_callback)
                markup.add(back_button)

        self.send_message(call, text=text, photo=photo, reply_markup=markup)

    def send_order_status_notification(self, chat_id, order_id, text=None):
        order = self.data.get_order(where={"OrderID":order_id})[0]
        
        # if text is passed through parameter
        if text:
            pass
        #new order
        elif order.Status == 1 and order.RedactionComment == None:
            text = self.data.message.order_notification_new
        #else
        else:
            text = self.data.get_order_status(where={"StatusID":order.Status})[0].Notification

        button = self.create_order_description_button(order, self_destruction=True)
        markup = InlineKeyboardMarkup()
        markup.add(button)

        self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    def send_confirmation(self, call, order_id, completion=False, rejection=False):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        self.bot.delete_message(chat_id, message_id)

        confirm_btn_text = "✅"
        reject_btn_text = "❌"
        markup = InlineKeyboardMarkup()

        if completion is True:
            text = self.data.message.order_completion_confirmation
            confirm_btn_callback = self.form_order_callback(action="ConfirmationInstruction", order_id=order_id, 
                                                            prev_msg_action="Edit")
        if rejection is True:
            text = self.data.message.order_rejection_confirmation
            confirm_btn_callback = self.form_order_callback(action="RejectReason", order_id=order_id, 
                                                            prev_msg_action="Edit")
        confirm_button = InlineKeyboardButton(text=confirm_btn_text, callback_data=confirm_btn_callback)
        reject_btn_callback = self.form_order_callback(action="Description", order_id=order_id, prev_msg_action="Delete")
        reject_button = InlineKeyboardButton(text=reject_btn_text, callback_data=reject_btn_callback)

        markup.add(confirm_button, reject_button)

        self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    def send_confirmation_instruction(self, call, order_id, delete=True):
        chat_id = call.message.chat.id
        if delete:
            self.bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        text = self.data.message.order_completion_confirmation_instruction

        self.bot.send_message(chat_id=chat_id, text=text)
        self.bot.register_next_step_handler_by_chat_id(chat_id, callback=self.process_order_confirmation,
                                                       chat_id_=chat_id, order_id=order_id)

    def send_reject_reason(self, call, order_id):

        text = self.data.message.order_choose_rejection_reason
        markup = InlineKeyboardMarkup()

        reasons = self.data.message.button_owner_reject_reasons
        for index, reason in enumerate(reasons):
            btn_text = reason
            btn_callback = self.form_redaction_callback(action="CloseOrder", order_id=order_id, rejection_reason_index=index)
            btn = InlineKeyboardButton(text=btn_text, callback_data=btn_callback)
            markup.add(btn)

        self.send_message(call=call, text=text, reply_markup=markup)

    def process_order_confirmation(self, message, **kwargs):
        chat_id = kwargs["chat_id_"]
        order_id = kwargs["order_id"]

        # if owner doesn't FORWARD a post
        if message.forward_from_chat is None or message.forward_from_chat.type != "channel":
            self.send_confirmation_instruction(chat_id, order_id, delete=False)
            return

        # collect all required info about post
        content_type = message.content_type
        post_id = message.forward_from_message_id
        try:
            post_text = message.text if content_type == "text" else message.caption
        except: # if owner forward a message that does not contain neither photo or text
            self.send_confirmation_instruction(chat_id, order_id, delete=False)
        post_time = datetime.fromtimestamp(message.forward_date)
        post_link = f"https://t.me/{message.forward_from_chat.username}/{post_id}"
        post_views = 0

        # update data in Database
        self.data.add_post_statistic(post_id=post_id, post_link=post_link, post_text=post_text,
                                     views_count=post_views, post_time=post_time)
        post_statistic_id = self.data.get_post_statistic(order_by={"PostStatisticID":"ASC"})[-1].PostStatisticID
        self.data.update_order(set_={"PostStatisticID":post_statistic_id}, where={"OrderID":order_id})         

        # create button "Send to redaction" and send it to owner
        text = self.data.message.order_send_to_redaction_check
        markup = InlineKeyboardMarkup()
        send_to_redaction_btn_text = self.data.message.button_order_send_to_redaction
        send_to_redaction_btn_callback = self.form_redaction_callback(action="CheckOrder", order_id=order_id)
        send_to_redaction_btn = InlineKeyboardButton(text=send_to_redaction_btn_text, callback_data=send_to_redaction_btn_callback)
        markup.add(send_to_redaction_btn)

        self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)      

    def get_all_orders(self, owner):
        """GET ALL ORDERS WHERE STATUS > 0
            RETURN
            ------
            list:
                list of valid orders
        """
        orders_list = list()
        channels = self.data.get_channel(where={"OwnerID":owner.OwnerID})

        for channel in channels:
            orders = self.data.get_order(where={"ChannelID":channel.ChannelID, "Status":0}, signs=["=", ">"])
            orders_list += [orders]

        return orders_list

    def form_order_description(self, order):
        #def get_delimiter(length=10):
        #    return "➖" * length + "\n"

        text = str()

        # AD text
        ad_text_title = self.data.message.order_description_text
        ad_text = order.Text.strip()
        text += f"{ad_text_title}\n{ad_text}\n\n"
        
        # Client comment
        ad_client_comment_title = self.data.message.order_description_client_comment
        ad_client_comment = order.Comment.strip()
        text += f"{ad_client_comment_title}\n{ad_client_comment}\n\n"

        # Post date
        ad_post_date_title = self.data.message.order_description_post_date
        ad_post_date = order.PostDate
        text += f"{ad_post_date_title}\n{ad_post_date}\n\n"

        # Price
        ad_price_title = self.data.message.order_description_price
        payment = self.data.get_payment(where={"OrderID":order.OrderID})[0]
        ad_price = payment.Amount
        text += f"{ad_price_title}\n{ad_price} UAH\n\n"

        # Order ID
        order_id_title = self.data.message.order_description_order_id
        order_id = order.OrderID
        text += f"{order_id_title}\n{order_id}\n\n"

        # Post Link
        if order.Status >= 2:
            post_statistic = self.data.get_post_statistic(where={"PostStatisticID":order.PostStatisticID})[0]
            post_statistic_link = post_statistic.PostLink
            text += f"<b>{self.data.message.order_description_post_link}</b> - {post_statistic_link}\n"

        # Order Status
        order_status_title = self.data.message.order_description_status
        order_status = self.data.get_order_status(where={"StatusID":order.Status})[0].Description
        text += f"{order_status_title}\n{order_status}\n\n"

        # Redaction Comment
        order_redaction_comment_title = self.data.message.order_description_redaction_comment
        order_redaction_comment = order.RedactionComment
        if order_redaction_comment is not None:
            text += f"{order_redaction_comment_title}\n{order_redaction_comment}\n\n"

        # Owner Comment
        order_owner_comment_title = self.data.message.order_description_owner_comment
        order_owner_comment = order.OwnerComment
        if order_redaction_comment is not None:
            text += f"{order_owner_comment_title}\n{order_owner_comment}\n\n"

        return text, order.Photo

    def form_notification_message(self, post_date, expired=False):
        if expired:
            text = self.data.message.order_notification_expired
        else:
            days_left = (post_date - date.today()).days

            if days_left == 0:
                text = self.data.message.order_notification_day_today
            else:
                text = f"{self.data.message.order_notification_days_left} - {days_left}"
        return text

    def create_order_description_button(self, order, self_destruction=False):
        def get_status_emoji(order_status):
            if order_status <= -1:
                return "✖️"
            if order_status < 2:
                return "🕐"
            if order_status == 2:
                return "📝"
            if order_status == 3:
                return "✅"
        def cut_channel_name(name, length=25):
            if len(name) > length:
                cut_name = name[:length] + "..."
                return cut_name
            return name
        channel = self.data.get_channel(where={"ChannelID":order.ChannelID})[0]

        ch_name = cut_channel_name(name=channel.Name.strip())
        emoji = get_status_emoji(order_status=order.Status)
        btn_text = f"{ch_name} {emoji}"

        prev_msg_action = "Delete" if self_destruction else "None"
        callback = self.form_order_callback(action="Description", order_id=order.OrderID, prev_msg_action=prev_msg_action)

        return InlineKeyboardButton(text=btn_text, callback_data=callback)