import pyodbc
from datetime import timedelta, date, datetime
import error_logging

class Data:
    def __init__(self, bot):
        self.REDACTION_CHAT_ID = -1001378510647
        self.bot = bot

        self.message = Message()
        self.dbo = Dbo(bot=bot)

    def get_channel(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_channel, values=col,
                                     where=where, sign=signs, order_by=order_by) 

        return rows

    def add_channel(self, link, name, subscribers=0, price=0,
                    photo="None", description="None", 
                    tag_id=None, statistic_id=None, owner_id=None, status=0,
                    register_date=date.today()):
        values = [link, name, subscribers, price, photo, description, statistic_id, tag_id, owner_id, status, register_date]

        self.dbo.add_value(self.dbo.table_channel, *values)

    def update_channel(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_channel, column=col, value=value,
                              where=where, where_value=where_value)
    
    def get_channel_stats(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_channel_stats, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_channel_stats(self, one_post, one_post_last_day, er, er_last_day): 
        values = [one_post, one_post_last_day, er, er_last_day]

        self.dbo.add_value(self.dbo.table_channel_stats, *values)
        
    def update_channel_stats(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_channel_stats, column=col, value=value,
                              where=where, where_value=where_value)

    def get_client(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_client, values=col,
                                     where=where, sign=signs, order_by=order_by) 

        return rows

    def add_client(self, chat_id, username, name, 
                   surname, register_date, last_interaction_time):
        values = [chat_id, username, name, surname, register_date, last_interaction_time]

        self.dbo.add_value(self.dbo.table_client, *values)

    def update_client(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_client, column=col, value=value,
                              where=where, where_value=where_value)

    def get_order(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_order, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_order(self, client_id, channel_id, text, photo, 
                  comment, post_date, order_date, redaction_comment=None, 
                  status=0, owner_comment=None, post_statistic_id=None):
        values = [client_id, channel_id, text, photo, 
                  comment, post_date, order_date, redaction_comment, 
                  status, owner_comment, post_statistic_id]

        self.dbo.add_value(self.dbo.table_order, *values)
        
    def update_order(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_order, column=col, value=value,
                              where=where, where_value=where_value)

    def get_post_statistic(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_post_statistic, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_post_statistic(self, post_id, post_link, post_text, views_count, 
                           post_time, channel_link=None, subscribers_on_start=None, 
                           subscribers_in_half_day=None, subscribers_in_day=None):
        values = [post_id, post_link, post_text, views_count, 
                  post_time, channel_link, subscribers_on_start, 
                  subscribers_in_half_day, subscribers_in_day]

        self.dbo.add_value(self.dbo.table_post_statistic, *values)
        
    def update_post_statistic(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_post_statistic, column=col, value=value,
                              where=where, where_value=where_value)

    def get_payment(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_payment, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_payment(self, order_id, order_reference, reason, 
                    amount, currency, created_date, processing_date, 
                    card_pan, card_type, issuer_bank_country, 
                    issuer_bank_name, transaction_status, refund_amount,
                    fee, merchant_signature):
        values = [order_id, order_reference, reason, 
                  amount, currency, created_date, processing_date, 
                  card_pan, card_type, issuer_bank_country, 
                  issuer_bank_name, transaction_status, refund_amount,
                  fee, merchant_signature]

        self.dbo.add_value(self.dbo.table_payment, *values)

    def update_payment(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_payment, column=col, value=value,
                              where=where, where_value=where_value)

    def get_order_status(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_order_status, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def get_channel_status(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_channel_status, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def get_owner(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_owner, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def add_owner(self, chat_id, nickname, name, 
                  surname, register_date, last_interaction_time):
        values = [chat_id, nickname, name, surname, 
                  register_date, last_interaction_time]

        self.dbo.add_value(self.dbo.table_owner, *values)
        
    def update_owner(self, set_=dict(), where=dict()):
        col = [[k] for k, v in set_.items()]
        value = [[v] for k, v in set_.items()]
        where, where_value = [[k, v] for k, v in where.items()][0]
        self.dbo.update_value(table=self.dbo.table_owner, column=col, value=value,
                              where=where, where_value=where_value)

    def get_tag(self, col=["*"], where=None, signs=["="], order_by=None):
        rows = self.dbo.select_table(table=self.dbo.table_tag, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

    def get_multiple_tables(self, tables:list, join_type="Right", col=["*"], where=None, signs=["="], order_by=None):
        table_string = f"[{tables[0]}] "

        table_index = 0
        while table_index < len(tables)-1:
            table_name_1 = tables[table_index]
            table_name_2 = tables[table_index+1]

            table_string += (f"{join_type} "
                             f"JOIN [{table_name_2}] "
                             f"ON [{table_name_1}].{table_name_1}ID = [{table_name_2}].{table_name_1}ID "
            )

            table_index += 1
        rows = self.dbo.select_table(table=table_string, values=col,
                                     where=where, sign=signs, order_by=order_by) 
        return rows

class Dbo:

    def __init__(self, bot):
        self.bot = bot
        self._init_table_names()
        self._connect_to_database()
    
    def _connect_to_database(self):
        #Computer DESKTOP-2IT0PLT
        #Laptop   DESKTOP-4T7IRV2
        print("Connecting to database...")
        try:
            self.connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                        'Server=104.154.69.146;'
                                        'Database=FastDeal;'
                                        'uid=sqlserver;'
                                        'pwd=zeOrd@;')
            print("Database connected succesfully!")
        except:
            raise ConnectionError
                      
        self.cursor = self.connection.cursor() 

    def _init_table_names(self):
        self.table_channel = "Channel"
        self.table_channel_status = "Channel_Status"
        self.table_channel_stats = "Channel_Statistic"
        self.table_client = "Client"
        self.table_order = "Order"
        self.table_payment = "Payment"
        self.table_post_statistic = "Post_Statistic"
        self.table_order_status = "Order_Status"
        self.table_owner = "Owner"
        self.table_tag = "Tag"

    def select_table(self, table, values, sign, where=None, order_by=None):
        select_clause = str()

        # Values
        for value in values:
            if value != "*":
                select_clause += "[{}], ".format(value)
            else:
                select_clause += "{}, ".format(value)
        select_clause = select_clause[:-2]
        
        # Where clause
        where_clause = str()
        if where is not None:
            where_clause = "WHERE "
            index = 0
            for key, value in where.items():
                if not isinstance(value, int) and not isinstance(value, date):
                    value = "N'{}%'".format(value)
                    where_clause += "{} LIKE {} AND ".format(key, value)
                else:
                    if isinstance(value, datetime):
                        date_time = value.strftime("%Y-%m-%d %H:%M:%S")
                        value = f"'{date_time}', "
                    elif isinstance(value, date):
                        value = f"'{str(value)}'"
                    where_clause += "{} {} {} AND ".format(key, sign[index], value)
                index += 1
            where_clause = where_clause[:-4]

        # Order By clause
        order_by_clause = str()
        if order_by is not None:
            value, direction = [[k, v] for k, v in order_by.items()][0]
            order_by_clause = f"ORDER BY {value} {direction}"

        table = f"[{table}]" if "[" not in table else table
        query = """ SELECT {}
                    FROM {}
                    {}
                    {}""".format(select_clause, table, where_clause, order_by_clause)
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except:
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(),
                                                  additional_info=query)
            return list()

        return rows

    def add_value(self, table, *values):
        value = str()
        for item in values:
            if item == None:
                value += "Null, "
            elif isinstance(item, datetime):
                date_time = item.strftime("%Y-%m-%d %H:%M:%S")
                value += f"'{date_time}', "
            elif isinstance(item, date):
                value += f"'{str(item)}', "
            elif isinstance(item, int) or isinstance(item, float):
                value += "{}, ".format(item)
            else:
                item = item.replace("'", "`")
                value += "N'{}', ".format(item)
        value = value[:-2] #erase , in the end

        query = """ INSERT INTO [{}]
                    VALUES ({})""".format(table, value)
        
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("{} added succesfully!".format(table))
        except:
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(),
                                                  additional_info=query)
            print("New {} not added(((".format(table))

    def update_value(self, table, column, value, where, where_value):
        
        values = str()
        for col, val in zip(column, value):
            if val[0] == None:
                values += f"{col[0]} = Null, "
            elif  isinstance(val[0], datetime):
                date_time = val[0].strftime("%Y-%m-%d %H:%M:%S")
                values += f"{col[0]} = '{date_time}', "
            elif isinstance(val[0], date):
                values += f"{col[0]} = '{str(val[0])}', "
            elif not isinstance(val[0], int):
                values += f"{col[0]} = N'{val[0]}', "
            else:
                values += f"[{col[0]}] = {val[0]}, "
        values = values[:-2]

        if not isinstance(where_value, int):
            where_value = "N'{}'".format(where_value)
        
        query = """ UPDATE [{}]
                    SET {}
                    WHERE [{}] = {}""".format(table, values, where, where_value)

        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("{} {} updated succesfully!".format(table, column))
        except:
            error_logging.send_error_info_message(bot=self.bot, current_frame=error_logging.currentframe(),
                                                  additional_info=query)
            print("{} {} failed to update(((".format(table, column))

#TO DO
#transfer to sql later
class Message:
    def __init__(self):
        self._init_messages()

    def _init_messages(self):
        self.start_registered_false = ("Вас відає FastDeal Bot для власників!\n"
                                       
                                      )
        self.start_registered_true = "Вас відає FastDeal Bot для власників!\n"


        self.channel_confirm = ("Щоб розпочати отримувати пропозиції реклами на ваші канали, потрібно підтвердити, що ви є його справжнім власником.\n"
                                "Для цього напишіть слово <b>REGISTER</b> нашій підтримці @onAzart та очікуйте подальших інструкцій."
                               )
        self.channel_not_exist = ("Такого каналу не існує!\n"
                                  "Введіть існуючий канал!"
                                 )
        self.channel_not_channel = ("Схоже на те, що це введений вами канал насправді не канал🤪\n"
                                    "Введіть існуючий канал!"
                                   )
        self.channel_already_registered = ("Схоже на те, що це введений вами канал вже зареєстрований\n"
                                           "Введіть інший канал!"
                                          )

        #REDACTION
        self.redaction_order_sent_to_owner = "Замовлення надіслано власнику!"
        self.redaction_order_completion_rejected = "Замовлення відправлено на доопрацювання!"
        self.redaction_reject_reason = "Введіть причину відказу"
        self.redaction_channel_registered = "Зареєстровано новий канал:\n"
        self.redaction_command_error = "Ти не маєш права це робити!"


        #ORDER
        self.order_description_text = "<i>Текст</i>"
        self.order_description_client_comment = "<i>Коментар замовника</i>"
        self.order_description_redaction_comment = "<i>Коментар редакції</i>"
        self.order_description_owner_comment = "<i>Коментар власника</i>"
        self.order_description_status = "<i>Статус:</i>"
        self.order_description_post_date = "<i>Замовлення на дату</i>"
        self.order_description_price = "<i>Ціна</i>"
        self.order_description_order_id = "<i>ID замовлення</i>"
        self.order_notification_new = "Нове замовлення!"
        self.order_notification_rejected = "Замовлення не виконано!"
        self.order_notification_completed = "Замовлення виконано успішно!"
        self.order_notification_expired = ("Ти не виконав замовлення!\n"
                                           "Якщо таке повториться, то мені прийдеться тебе заблокувати☹️"
        )
        self.order_notification_days_left = "Залишилось днів щоб виконати замовлення"
        self.order_notification_day_today = "Прийшов час виконати замовлення!"
        self.order_list = "Список усіх замовлень:"
        self.order_completion_confirmation = "Ви підтверджуєте, що виконали дане замовлення?"
        self.order_rejection_confirmation = "Ви впевнені, що відмовляєтесь від замовлення?"
        self.order_completion_confirmation_instruction = ("Я хочу подивитись на цей пост!\n"
                                                          "Надішли мені його сюди"
        )
        self.order_send_to_redaction_check = "Нажміть на кнопку щоб відправити замовлення на перевірку!"
        self.order_sent_to_redaction_check = "Ви позначили дане замовлення як виконане!\nПісля перевірки редакцією вам будуть зараховані кошти."
        self.order_choose_rejection_reason = "Виберіть причину відказу:"

        #CHANNEL
        self.channel_list = "Список ваших каналів:"
        self.channel_description_description = "🗒<i><u>Опис каналу</u></i>"
        self.channel_description_subs = "👥<i>Підписники</i>"
        self.channel_description_price = "💰<i>Ціна</i>"
        self.channel_description_post_views = "👁<i><u>Переглядів на пост</u></i>"
        self.channel_description_post_views_last_seven_days = "🔹<i>За останній тиждень</i>"
        self.channel_description_post_views_last_day = "🔸<i>За останні 24 години</i>"
        self.channel_description_er = "📈<i><u>ER</u></i> (процент підписників, яка взаємодіяла з постами)"
        self.channel_description_er_last_seven_days = "🔹<i>Тижневий</i>"
        self.channel_description_er_last_day = "🔸<i>Денний</i>"
        self.channel_add_input_name = ("Напишіть назву вашого каналу, на який буде здійснюватись покупка реклами.\n"
                                       "Назву каналу вказувати у форматі <b>@name</b>"
                                       )
        self.channel_input_photo = "Киньте фото"
        self.channel_input_price = "Введіть ціну (UAH)"
        self.channel_photo_changed = "Фото успішно змінене!"
        self.channel_price_changed = "Ціна успішно змінена!"
        self.channel_stats_changed = "Статистика успішно змінена!"
        self.channel_tag_choose = (
            "Оберіть одну з наступних категорій\n"
            "Поточна категорія - "
        )
        self.channel_statistic_refreshed = "Статитистика оновлена"

        ##############    BUTTONS  #####################
        self.button_owner_reject_reasons = ["Не підходить дата", "Контент реклами"]
        self.button_owner_order_rejected = "Ви успішно відмовились від замовлення!і"

        self.button_channel_add_new = "Додати канал"
        self.button_channel_forbidden_topics = "❗️Заборонені теми❗️"
        self.button_channel_statistic = "Статистика"
        self.button_channel_reviews = "Відгуки"
        self.button_channel_activate = "Активувати"
        self.button_channel_disactivate = "Дезактивувати"
        self.button_channel_change_photo = "Змінити фото"
        self.button_channel_change_tag = "Змінити тег"
        self.button_channel_change_description = "Змінити опис"
        self.button_channel_change_price = "Змінити ціну"
        self.button_channel_change_stats = "Оновити статистику"

        self.button_order_send_to_redaction = "Надіслати редакції"
        
        ##############    ETC  #####################

        self.wait = "Один момент і все буде!"
        self.oops = "Щось пішло не так :("
        self.under_development = "В розробці"
        self.delete_error = "Старі повідомлення неможливо видалити"

    def redaction_finished_order(self, order_id):
        """
        'FINISHED' - notification for another bot
        """
        msg = f"/FINISHED_{order_id}"
        return msg

    def channel_changed_status(self, channel, activate=False, disactivate=False):
        action = "<b>активовано</b>" if activate else "<b>дезактивовано</b>"

        return f"Ваш канал {channel.Name} {action}!"