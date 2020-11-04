from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from sections.section import Section
from datetime import datetime

class Account(Section):

    WITHDRAW_MINIMUM = 1

    def __init__(self, data):
        super().__init__(data=data)
        
    def process_callback(self, call):
        #Account;{action};{card_id};{withdraw_id}
        action = call.data.split(";")[1]
        chat_id = call.message.chat.id

        if action == "Cabinet":
            self.send_cabinet_menu(call)

        elif action == "Balance":
            self.send_balance_menu(call)

        # Cash out Menu
        elif action == "CashOut":
            self.send_cash_out_menu(call)

        elif action == "AddCard":
            self.send_add_card_request(chat_id)

        elif action == "Withdraw":
            card_id = int(call.data.split(";")[2])
            self.send_card_to_withdraw_confirmation_request(chat_id, card_id)

        # In redaction
        elif action == "ConfirmWithdraw":
            withdraw_id = int(call.data.split(";")[3])
            self.send_withdraw_completed_message(call, withdraw_id)

        else:
            self.in_development(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_cabinet_menu(self, call):
        chat_id = call.message.chat.id

        cabinet_text = self._form_text_cabinet_menu(chat_id=chat_id)
        cabinet_markup = self._create_markup_cabinet_menu()

        self.send_message(call, text=cabinet_text, reply_markup=cabinet_markup)

    def send_balance_menu(self, call):
        chat_id = call.message.chat.id
        
        balance_text = self._form_text_balance_menu(chat_id)
        balance_markup = self._create_markup_balance_menu()

        self.send_message(call, text=balance_text, reply_markup=balance_markup)

    def send_cash_out_menu(self, call):
        chat_id = call.message.chat.id
        
        cash_out_text = self._form_text_cash_out_menu()
        cash_out_markup = self._create_markup_cash_out_menu(chat_id)

        self.send_message(call, text=cash_out_text, reply_markup=cash_out_markup)

    def send_withdraw_request_to_redaction_menu(self, withdraw_id):

        withdraw_request_to_redaction_text = self._form_text_withdraw_request_to_redaction(withdraw_id=withdraw_id)
        withdraw_request_to_redaction_markup = self._create_markup_withdraw_request_to_redaction(withdraw_id=withdraw_id)
        
        self.bot.send_message(chat_id=self.data.REDACTION_CHAT_ID, text=withdraw_request_to_redaction_text,
                              reply_markup=withdraw_request_to_redaction_markup, parse_mode="HTML")

    def send_add_card_request(self, chat_id):
        card_request_text = "Введіть номер своєї банківської карти (16 цифр)"
        self.bot.send_message(chat_id, text=card_request_text)

        self.bot.register_next_step_handler_by_chat_id(chat_id, callback=self.process_add_card)

    def send_card_to_withdraw_confirmation_request(self, chat_id, card_id):
        if self.check_withdraw_minimum(chat_id=chat_id) is False:
            return

        card_number = self.data.get_owner_card(where={"OwnerCardID":card_id})[0].CardNumber

        card_to_withdraw_confirmation_text = (f"Щоб підтвердити вивід коштів на\n"
                             f"💳<b>{card_number[:4]}****{card_number[12:]}</b>\n"
                             f"відправ мені остаанні 4 цифри номеру карти.")
        self.bot.send_message(chat_id, text=card_to_withdraw_confirmation_text, parse_mode="HTML")

        self.bot.register_next_step_handler_by_chat_id(chat_id, callback=self.process_card_to_withdraw_confirmation, 
                                                       card_id=card_id, card_number=card_number)

    def send_withdraw_completed_message(self, call, withdraw_id):
        withdraw = self.data.get_withdraw(where={"WithdrawID":withdraw_id})[0]
        owner_card = self.data.get_owner_card(where={"OwnerCardID":withdraw.OwnerCardID})[0]
        owner = self.data.get_owner(where={"OwnerAccountID":owner_card.OwnerAccountID})[0]
        
        # Update withdraw status
        self.data.update_withdraw(set_={"Status":1}, where={"WithdrawID":withdraw.WithdrawID})

        # In Redaction
        redaction_text = f"{call.message.text}\n\n<b>Статус - виконано</b>"
        self.send_message(call, text=redaction_text)

        # in Owner
        owner_text = "На вашу карту успішно зараховані кошти!"
        self.bot.send_message(chat_id=owner.ChatID, text=owner_text)

    

    def process_add_card(self, message, **kwargs):
        def check_card_existence(card_number):
            if len(self.data.get_owner_card(where={"CardNumber":card_number})) != 0:
                self.bot.send_message(chat_id, text="Цей номер карти вже зереєстровано!")
                self.send_add_card_request(chat_id=chat_id)
                return True
            return False

        chat_id = message.chat.id

        # Try again if user sent not a text
        if message.content_type != "text":
            self.send_add_card_request(chat_id=chat_id)
            return
        else:
            try:
                card_number = str(int(message.text))
            # Try again if user sent not digits
            except:
                self.send_add_card_request(chat_id=chat_id)
                return
            # Try again if user sent wrong card format
            if len(card_number) != 16:
                self.send_add_card_request(chat_id=chat_id)
                return

            # Send Success message if card was added
            # HERE *add card to DB* 
            owner_account_id = self.data.get_multiple_tables(tables=["OwnerAccount", "Owner"], 
                                                             where={"ChatID":chat_id})[0].OwnerAccountID
            if check_card_existence(card_number=str(card_number)):
                return
            self.data.add_owner_card(card_number=str(card_number), owner_account_id=owner_account_id)

            success_text = f"Ваша карта <b>{card_number}</b> успішно добавлена!"
            markup = InlineKeyboardMarkup()
            back_btn_callback = self.form_account_callback(action="CashOut", prev_msg_action="Edit")
            back_btn = self.create_back_button(back_btn_callback, custom_btn_text="Продовжити")
            markup.add(back_btn)
            self.bot.send_message(chat_id, text=success_text, reply_markup=markup, parse_mode="HTML")

    def process_card_to_withdraw_confirmation(self, message, **kwargs):
        card_number = kwargs["card_number"]
        card_id = kwargs["card_id"]
        chat_id = message.chat.id

        if message.content_type != "text":
            self.send_card_to_withdraw_confirmation_request(chat_id=chat_id, card_id=card_id)
            return
        else:
            last_4_card_digits = card_number[12:]
            if message.text.strip() == last_4_card_digits:
                correct_card_text = ("🕐Зарахування коштів буде здійснене протягом 12 годин"
                                     "\nДякую, що ти зі мною!"
                                    )  
                withdraw_id = self.add_new_withdraw(card_id=card_id)
                self.bot.send_message(chat_id, text=correct_card_text, parse_mode="HTML")
                self.send_withdraw_request_to_redaction_menu(withdraw_id=withdraw_id)
                
            else:
                incorrect_card_text = "Схоже ти допустив помилку :(\nСпробуй ще разок!"
                self.bot.send_message(chat_id, text=incorrect_card_text, parse_mode="HTML")
                self.send_card_to_withdraw_confirmation_request(chat_id=chat_id, card_id=card_id)


    def check_withdraw_minimum(self, chat_id):
        owner = self.data.get_owner(where={"ChatID":chat_id})[0]
        owner_account = self.data.get_owner_account(where={"OwnerAccountID":owner.OwnerAccountID})[0]
        
        owner_account_balance = owner_account.Balance

        if owner_account_balance < self.WITHDRAW_MINIMUM:
            to_earn = self.WITHDRAW_MINIMUM - owner_account_balance
            lack_of_funds_text = ("Недостатня кількість коштів на твоєму рахунку для здійснення операції.\n"
                                 f"Мінімальна сума для виведення - <b>{self.WITHDRAW_MINIMUM}грн</b>\n" 
                                 f"\nТобі потрібно ще <b>{to_earn}</b>!"
                                 )
            self.bot.send_message(chat_id, text=lack_of_funds_text, parse_mode="HTML")
            return False
        else:
            return True

    def add_new_withdraw(self, card_id):
        # get current balance of OwnerAccount
        owner_account_id = self.data.get_owner_card(where={"OwnerCardID":card_id})[0].OwnerAccountID
        owner_account_balance = self.data.get_owner_account(where={"OwnerAccountID":owner_account_id})[0].Balance

        # get require data for withdraw
        amount = owner_account_balance
        date = datetime.now()
        status = 0
        owner_card_id = card_id

        # add new withdraw to Database
        self.data.add_withdraw(amount, date, status, owner_card_id)
        withdraw_id = self.data.get_withdraw(order_by={"WithdrawID":"Desc"})[0].WithdrawID

        # annulement of OwnerAccount balance
        self.data.update_owner_account(set_={"Balance":0},
                                       where={"OwnerAccountID":owner_account_id})

        return withdraw_id


    def _create_markup_cabinet_menu(self):
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

        # Balance button
        balance_btn_text = self.data.message.button_account_balance
        balance_btn_callback = self.form_account_callback(action="Balance", prev_msg_action="Edit")
        balance_btn = InlineKeyboardButton(text=balance_btn_text, callback_data=balance_btn_callback)
        markup.add(balance_btn) 

        # Back to start page button
        back_btn_callback = self.form_main_callback(action="Start", prev_msg_action="Edit")
        back_btn = self.create_back_button(callback_data=back_btn_callback)
        markup.add(back_btn)

        return markup

    def _create_markup_balance_menu(self):
        markup = InlineKeyboardMarkup()

        # Cash out button
        cash_out_btn_text = self.data.message.button_account_cash_out
        cash_out_btn_callback = self.form_account_callback(action="CashOut", prev_msg_action="Edit")
        cash_out_btn = InlineKeyboardButton(text=cash_out_btn_text, callback_data=cash_out_btn_callback)
        markup.add(cash_out_btn)

        # Back to cabinet page button
        back_btn_callback = self.form_account_callback(action="Cabinet", prev_msg_action="Edit")
        back_btn = self.create_back_button(callback_data=back_btn_callback)
        markup.add(back_btn)

        return markup

    def _create_markup_cash_out_menu(self, chat_id):
        owner = self.data.get_owner(where={"ChatID":chat_id})[0] # todo - get cards list
        owner_cards = self.data.get_multiple_tables(tables=["OwnerAccount", "OwnerCard"], 
                                                    where={"OwnerAccount.OwnerAccountID":owner.OwnerAccountID})

        markup = InlineKeyboardMarkup()

        # Card buttons
        for card in owner_cards:
            card_number = card.CardNumber
            card_btn_text = f"{card_number[:4]}****{card_number[12:]}"
            card_btn_callback = self.form_account_callback(action="Withdraw", card_id=card.OwnerCardID, prev_msg_action="Edit")
            card_btn = InlineKeyboardButton(text=card_btn_text, callback_data=card_btn_callback)
            markup.add(card_btn)

        # Add card button
        add_card_btn_text = self.data.message.button_account_add_card
        add_card_btn_callback = self.form_account_callback(action="AddCard", prev_msg_action="Edit")
        add_card_btn = InlineKeyboardButton(text=add_card_btn_text, callback_data=add_card_btn_callback)
        markup.add(add_card_btn)

        # Back to cabinet page button
        back_btn_callback = self.form_account_callback(action="Balance", prev_msg_action="Edit")
        back_btn = self.create_back_button(callback_data=back_btn_callback)
        markup.add(back_btn)

        return markup

    def _create_markup_withdraw_request_to_redaction(self, withdraw_id):

        markup = InlineKeyboardMarkup()

        withdraw_completed_btn_text = "Підтвердити вивід"
        withdraw_completed_btn_callback = self.form_account_callback(action="ConfirmWithdraw",
                                                                     withdraw_id=withdraw_id,
                                                                     prev_msg_action="Edit")
        withdraw_completed_btn = InlineKeyboardButton(text=withdraw_completed_btn_text,
                                                      callback_data=withdraw_completed_btn_callback)
        markup.add(withdraw_completed_btn)

        return markup
        


    def _form_text_cabinet_menu(self, chat_id):
        owner = self.data.get_owner(where={"ChatID":chat_id})[0]
        channels = self.data.get_channel(where={"OwnerID":owner.OwnerID})

        text = "".join(("Привіт <b>{}</b>!\n",
                        "\n{}"))

        if len(channels) == 0:
            additional_info = "".join(("Щоб розпочати отримувати замовлення перейдіть до вкладки ",
                                       "<b>Мої канали</b> та додайте свій перший канал!"))
        else:
            additional_info = "*якась додаткова інфа для зарєстрованого користувача*"

        text = text.format(owner.Name, additional_info)

        return text

    def _form_text_balance_menu(self, chat_id):
        owner = self.data.get_owner(where={"ChatID":chat_id})[0] 
        owner_account_balance = self.data.get_owner_account(where={"OwnerAccountID":owner.OwnerAccountID})[0].Balance

        text = f"Твій баланс - <b>{owner_account_balance} грн</b>"

        return text

    def _form_text_cash_out_menu(self):
        text = "Виберіть призначення платежу:"

        return text

    def _form_text_withdraw_request_to_redaction(self, withdraw_id):
        withdraw = self.data.get_withdraw(where={"WithdrawID":withdraw_id})[0]
        owner_card = self.data.get_owner_card(where={"OwnerCardID":withdraw.OwnerCardID})[0]
        owner_account = self.data.get_owner_account(where={"OwnerAccountID":owner_card.OwnerAccountID})[0]
        owner = self.data.get_owner(where={"OwnerAccountID":owner_card.OwnerAccountID})[0]

        withdraw_request_text = ("<b>Новий вивід!</b>\n\n"
                                 f"Користувач - @{owner.Nickname}\n"
                                 f"Сума - {withdraw.Amount}\n"
                                 f"Карта - {owner_card.CardNumber}"
                                )
        
        return withdraw_request_text