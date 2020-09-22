from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta, timezone
from time import sleep
import textwrap
from sections.section import Section

class Channel(Section):

    def __init__(self, data, client):
        super().__init__(data=data)
        self.client = client
        
        self.MAX_CHANNEL_LENGTH = 25
        self.REDACTION_CHAT_ID = self.data.REDACTION_CHAT_ID#-1001153596317

    def process_callback(self, call):
        #Channel;{action};{channel_id}
        action, channel_id = call.data.split(";")[1:3]
        chat_id = call.message.chat.id

        if action == "Select":
            self.send_channel_content(chat_id=chat_id, channel_id=channel_id)

        elif action == "ForbiddenTopics":
            self.send_channel_forbidden_topics(call=call, channel_id=channel_id)

        elif action == "Stats":
            self.send_channel_stats(call=call, channel_id=channel_id)

        elif action == "Reviews":
            self.send_channel_reviews(call=call, channel_id=channel_id)

        elif action == "Activate":
            self.change_channel_status(call=call, channel_id=channel_id, activate=True)

        elif action == "Disactivate":
            self.change_channel_status(call=call, channel_id=channel_id, disactivate=True)

        elif action == "Add":
            self.add_channel(call=call)

        elif action == "ChangePhoto":
            self.change_photo(chat_id=chat_id, channel_id=channel_id)

        elif action == "TagList":
            self.send_channel_tags_list(chat_id=chat_id, channel_id=channel_id)

        elif action == "ChangeTag":
            tag_id = call.data.split(";")[3]
            self.change_tag(call=call, channel_id=channel_id, tag_id=tag_id)

        elif action == "ChangeDescription":
            self.change_description(chat_id=chat_id, channel_id=channel_id)

        elif action == "ChangePrice":
            self.change_price(chat_id=chat_id, channel_id=channel_id)

        elif action == "UpdateStatisticChannel":
            self.update_statistic(call=call, channel_id=channel_id)

        elif action == "UpdateStatisticAll":
            self.update_statistic(call=call)

        elif action == "UpdateSubscribers": # Maybe better to update it every day
            pass

        else:
            self.oops(call)
            return

        self.bot.answer_callback_query(call.id)

    def send_channel_list(self, chat_id):
        if chat_id == self.data.REDACTION_CHAT_ID:
            channels = self.data.get_channel()
        else:
            owner = self.data.get_owner(where={"ChatID":chat_id})[0]
            channels = self.data.get_channel(where={"OwnerID":owner.OwnerID, "Status":0}, signs=["=", "<>"])

        text = self.data.message.channel_list
        markup = InlineKeyboardMarkup()

        #channel buttons
        for channel in channels:
            btn = self.create_channel_button(channel=channel)
            markup.add(btn)

        #add new channel button
        if chat_id != self.data.REDACTION_CHAT_ID:
            add_new_channel_button_text = self.data.message.button_channel_add_new
            add_new_channel_button_callback = self.form_channel_callback(action="Add")
            add_new_channel_button = InlineKeyboardButton(text=add_new_channel_button_text, callback_data=add_new_channel_button_callback)
            markup.add(add_new_channel_button)
        else:
            # change stats
            change_stats_btn_text = self.data.message.button_channel_change_stats
            change_stats_btn_callback = self.form_channel_callback(action="UpdateStatisticAll")
            change_stats_btn = InlineKeyboardButton(text=change_stats_btn_text, callback_data=change_stats_btn_callback)
            markup.add(change_stats_btn)

        #delete button
        markup.add(self.create_delete_button())

        self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    def send_channel_content(self, chat_id, channel_id):
        current_channel = self.data.get_channel(where={"ChannelID":channel_id})[0]
        
        text, photo = self.create_channel_description(channel=current_channel)
        markup = InlineKeyboardMarkup()

        #заборонені теми
        forbiden_topics_callback = self.form_channel_callback(action="ForbiddenTopics", channel_id=channel_id)
        forbiden_topics_text = self.data.message.button_channel_forbidden_topics
        forbiden_topics_btn = InlineKeyboardButton(text=forbiden_topics_text, callback_data=forbiden_topics_callback)
        markup.add(forbiden_topics_btn)

        #статистика & відгуки
        #statistic_url = self.data.get_channel(where={"ChannelID":channel_id}, get_inactive=True)[0].Stats
        #statistic_text = self.data.message.button_channel_statistic
        #if statistic_url != None:
        #    statistic_btn = InlineKeyboardButton(text=statistic_text, url=statistic_url.strip())
        #    markup.add(statistic_btn)

        #reviews_callback = self.form_channel_callback(action="Reviews", channel_id=channel_id)
        #reviews_text = self.data.message.button_channel_reviews
        #reviews_button = InlineKeyboardButton(text=reviews_text, callback_data=reviews_callback)
        #markup.add(reviews_button)

        # Activate & Disactivate channel
        if chat_id != self.REDACTION_CHAT_ID:
            if current_channel.Status == -1:
                activate_channel_btn_text = self.data.message.button_channel_activate
                activate_channel_btn_callback = self.form_channel_callback(action="Activate", channel_id=channel_id)
                activate_channel_btn = InlineKeyboardButton(text=activate_channel_btn_text, callback_data=activate_channel_btn_callback)
                markup.add(activate_channel_btn)
            else:
                disactivate_channel_btn_text = self.data.message.button_channel_disactivate
                disactivate_channel_btn_callback = self.form_channel_callback(action="Disactivate", channel_id=channel_id)
                disactivate_channel_btn = InlineKeyboardButton(text=disactivate_channel_btn_text, callback_data=disactivate_channel_btn_callback)
                markup.add(disactivate_channel_btn)

        # If called in Redaction then display special buttons
        if chat_id == self.REDACTION_CHAT_ID:
            redaction_buttons = self.create_redaction_buttons(channel=current_channel)
            for button in redaction_buttons:
                markup.add(button)

        # delete button
        markup.add(self.create_delete_button())

        # send message
        if photo is not None:
            self.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode="HTML")

    def send_channel_forbidden_topics(self, call, channel_id):
        under_dev = self.data.message.under_development
        self.bot.answer_callback_query(call.id, text=under_dev)

    def send_channel_stats(self, call, channel_id):
        under_dev = self.data.message.under_development
        self.bot.answer_callback_query(call.id, text=under_dev)

    def send_channel_reviews(self, call, channel_id):
        under_dev = self.data.message.under_development
        self.bot.answer_callback_query(call.id, text=under_dev)

    def send_channel_tags_list(self, chat_id, channel_id):
        tag_buttons_structure = [2, 2, 2, 2]
        tag_list = self.data.get_tag()[1:-1]

        markup = InlineKeyboardMarkup()

        channel = self.data.get_channel(where={"ChannelID":channel_id})[0]
        tag = self.data.get_tag(where={"TagID":channel.TagID})
        if len(tag) > 0:
            tag_name = tag[0].Name
        else:
            tag_name = "None"
        text = f"{self.data.message.channel_tag_choose}<b>{tag_name}</b>"

        markup = InlineKeyboardMarkup()
        tag_index = 0
        for row in tag_buttons_structure:
            btn_row = list()
            for tag in range(row):
                tag_name = tag_list[tag_index].Name
                tag_id = tag_list[tag_index].TagID
                callback = self.form_channel_callback(action="ChangeTag", channel_id=channel_id, tag_id=tag_id)
                tag_button = InlineKeyboardButton(text=tag_name, callback_data=callback)
                btn_row += [tag_button]
                tag_index += 1
            markup.add(*btn_row)

        markup.add(self.create_delete_button())
        self.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode="HTML")

    def add_channel(self, call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        text = self.data.message.channel_add_input_name

        self.bot.register_next_step_handler_by_chat_id(chat_id, callback=self.process_channel_register)

        self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=None, parse_mode="HTML")

    def change_channel_status(self, call, channel_id, activate=False, disactivate=False):
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        channel = self.data.get_channel(where={"ChannelID":channel_id})[0]
        owner = self.data.get_owner(where={"OwnerID":channel.OwnerID})[0]          

        if activate is True:
            self.data.update_channel(set_={"Status":1}, where={"ChannelID":channel_id})
            if chat_id == self.REDACTION_CHAT_ID:
                owner_notification_text = self.data.message.channel_changed_status(channel=channel, activate=True)
                self.bot.send_message(chat_id=owner.ChatID, text=owner_notification_text, parse_mode="HTML")

        if disactivate is True:
            self.data.update_channel(set_={"Status":-1}, where={"ChannelID":channel_id})
            if chat_id == self.REDACTION_CHAT_ID:
                owner_notification_text = self.data.message.channel_changed_status(channel=channel, activate=False)
                self.bot.send_message(chat_id=owner.ChatID, text=owner_notification_text, parse_mode="HTML")

        #delete channel description to refresh it
        self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        call.data = self.form_channel_callback(action="Select", channel_id=channel_id)
        self.send_channel_content(chat_id, channel_id)
    
    def change_photo(self, chat_id, channel_id):
        text = self.data.message.channel_input_photo

        self.bot.send_message(chat_id=chat_id, text=text)
        self.bot.register_next_step_handler_by_chat_id(chat_id, callback=self.process_change_photo,
                                                  chat_id_=chat_id, channel_id=channel_id)

    def change_tag(self, call, channel_id, tag_id):
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        self.data.update_channel(set_={"TagID":tag_id}, where={"ChannelID":channel_id})

        self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        self.send_channel_tags_list(chat_id=chat_id, channel_id=channel_id)

    def change_description(self, chat_id, channel_id):
        pass

    def change_price(self, chat_id, channel_id):
        text = self.data.message.channel_input_price

        self.bot.send_message(chat_id=chat_id, text=text)
        self.bot.register_next_step_handler_by_chat_id(chat_id, callback=self.process_change_price,
                                                  chat_id_=chat_id, channel_id=channel_id)

    def process_channel_register(self, message, **kwargs):
        chat_id = message.chat.id

        user_input = message.text

        #If command executed then reset
        if user_input[0] == '/': 
            self.bot.clear_step_handler(message)
            return

        #get channel name
        channel_name = user_input

        #get channel
        channel, text = self.client.get_channel(channel_name=channel_name)
        
        if channel is None:
            pass
        #if channel is already registered
        elif len(self.data.get_channel(where={"Link":channel_name})) >= 1:
            text = self.data.message.channel_already_registered
        #else add new channel to db
        else:
            channel_confirm_text = self.data.message.channel_confirm
            owner = self.data.get_owner(where={"ChatID":chat_id})[0]
            
            channel_description = channel.full_chat.about
            channel_link = channel_name
            channel_name = channel_link
            channel_subs = channel.full_chat.participants_count
            channel_photo = None
            owner_id = owner.OwnerID

            channel_statistic = self.form_channel_statistic(channel_name=channel_name, subscribers=channel_subs)
            self.data.add_channel_stats(one_post=channel_statistic[0], one_post_last_day=channel_statistic[1],
                                        er=channel_statistic[2], er_last_day=channel_statistic[3])
            statistic_id = self.data.get_channel_stats(order_by={"StatisticID":"ASC"})[-1].StatisticID

            self.data.add_channel(link=channel_link, name=channel_name, subscribers=channel_subs, 
                                  description=channel_description, owner_id=owner_id, photo=channel_photo,
                                  statistic_id=statistic_id)

            # bot send message of success
            self.bot.send_message(chat_id=chat_id, text=channel_confirm_text, parse_mode="HTML")
            # client send message with instructions
            self.client.send_register_instructions(owner_username=owner.Nickname)
            # bot send message about adding new channel to Redaction
            text = self.data.message.redaction_channel_registered + channel_name
            self.bot.send_message(chat_id=self.data.REDACTION_CHAT_ID, text=text)

            return

        message = self.bot.send_message(chat_id=chat_id, text=text)
        self.bot.register_next_step_handler(message, callback=self.process_channel_register)

    def process_change_photo(self, message, **kwargs):
        chat_id = kwargs["chat_id_"]
        channel_id = int(kwargs["channel_id"])

        if message.content_type == "photo":
            text = self.data.message.channel_photo_changed
            photo = message.json['photo'][0]['file_id']
            self.data.update_channel(set_={"Photo":photo}, where={"ChannelID":channel_id})

            self.bot.send_message(chat_id=chat_id, text=text)
            self.send_channel_content(chat_id, channel_id)
        else:            
            #If command executed then reset
            if message.content_type == "text":
                if message.text[0] == '/': 
                    self.bot.clear_step_handler(message)
                    return
            self.change_photo(chat_id, channel_id)

    def process_change_price(self, message, **kwargs):
        chat_id = kwargs["chat_id_"]
        channel_id = int(kwargs["channel_id"])

        if message.content_type == "text":
            #If command executed then reset
            if message.text[0] == '/': 
                self.bot.clear_step_handler(message)
                return
            try:
                price = int(message.text)
            except: # if price was a text than try again
                self.change_price(chat_id, channel_id)
                return
            text = self.data.message.channel_price_changed
            self.data.update_channel(set_={"Price":price}, where={"ChannelID":channel_id})

            self.bot.send_message(chat_id=chat_id, text=text)
            self.send_channel_content(chat_id, channel_id)
            return
        else:
            self.change_price(chat_id, channel_id)

    def update_statistic(self, call, channel_id=None):
        """Update statistic of the channel(s)
        
        Parameters
        ----------
        channel_id : int
            The ID of the channel. If None - update all channels.
        """
        chat_id = call.message.chat.id

        # if channel_id is passed update one channel
        if channel_id:
            channel_list = self.data.get_channel(where={"ChannelID":channel_id})
        # If channel_id is not passed update all channels
        else:
            channel_list = self.data.get_channel()

        message = self.bot.send_message(chat_id=chat_id, text=self.data.message.wait)
        self.bot.answer_callback_query(call.id, text=None)
            
        for channel in channel_list:   
            sleep(2)

            channel_name = channel.Link
            statistic_id = channel.StatisticID
            channel_id = channel.ChannelID

            self.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, 
                                  text=f"{channel.Name} is updating...")

            subscribers = self.bot.get_chat_members_count(channel_name)
            statistic = self.form_channel_statistic(channel_name=channel_name, subscribers=subscribers)

            # Update value
            try:
                # if there was no statistic - add it
                if statistic_id is None:
                    self.data.add_channel_stats(one_post=statistic[0], one_post_last_day=statistic[1],
                                                er=statistic[2], er_last_day=statistic[3])
                    statistic_id = self.data.get_channel_stats(order_by={"StatisticID":"ASC"})[-1].StatisticID
                    self.data.update_channel(set_={"StatisticID":statistic_id}, where={"ChannelID":channel_id})

                # otherwise - update it
                else:
                    self.data.update_channel_stats(set_={"OnePost":statistic[0], "OnePostLastDay":statistic[1],
                                                   "ER":statistic[2], "ERLastDay":statistic[3]}, 
                                                   where={"StatisticID":statistic_id})

                # update subscribers
                self.data.update_channel(set_={"Subscribers":subscribers}, where={"ChannelID":channel_id})
            except:
                self.bot.send_message(chat_id=chat_id, text=f"{success_update_text} failed to update!")
                continue

            success_update_text = f"{self.data.message.channel_statistic_refreshed} - {channel.Name}"
            self.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, 
                                  text=f"{success_update_text}")

            # Refresh channel page if it was one-channel-update
            if len(channel_list) == 1:
                self.bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
                self.send_channel_content(chat_id, channel_id)
                return
        
        self.bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, 
                                   text=f"Update is finished!")

    def create_channel_description(self, channel):
        def compress_string(string):
            return "\n".join(textwrap.wrap(string, 40, break_long_words=False))
        def get_delimiter(length=10):
            return " " * length + "\n"

        name = channel.Name.strip()
        link = channel.Link.strip()
        description = channel.Description.strip()
        price = channel.Price
        subscribers = channel.Subscribers
        photo = channel.Photo

        statistic = self.data.get_channel_stats(where={"StatisticID":channel.StatisticID})
        if len(statistic) > 0:
            statistic = statistic[0]
            stat_one_post = statistic.OnePost
            stat_one_post_last_day = statistic.OnePostLastDay
            stat_er = statistic.ER
            stat_er_last_day = statistic.ERLastDay
        else:
            statistic = None

        text = str()

        text += f"<b>{name}</b>\n"
        text += f"{link}\n"
        text += get_delimiter()

        
        text += f"{self.data.message.channel_description_description}:\n{compress_string(description)}\n"
        text += get_delimiter()

        text += f"{self.data.message.channel_description_subs} - {subscribers}\n"
        text += f"{self.data.message.channel_description_price} - {price} грн\n"

        if statistic:
            text += f"\n{self.data.message.channel_description_post_views}:\n"
            text += f"{self.data.message.channel_description_post_views_last_seven_days} - <b>{stat_one_post}</b>\n"
            text += f"{self.data.message.channel_description_post_views_last_day} - <b>{stat_one_post_last_day}</b>\n"
            
            text += f"\n{self.data.message.channel_description_er}:\n"
            text += f"{self.data.message.channel_description_er_last_seven_days} - <b>{stat_er}%</b>\n"
            text += f"{self.data.message.channel_description_er_last_day} - <b>{stat_er_last_day}%</b>\n"

        return text, photo

    def create_redaction_buttons(self, channel):
        channel_id = channel.ChannelID

        buttons = list()

        # activate or disactivate channel button
        channel_status = channel.Status
        if channel_status <= 0:
            activate_channel_btn_text = self.data.message.button_channel_activate
            activate_channel_btn_callback = self.form_channel_callback(action="Activate", channel_id=channel_id)
            activate_channel_btn = InlineKeyboardButton(text=activate_channel_btn_text, callback_data=activate_channel_btn_callback)
            buttons += [activate_channel_btn]
        else:
            disactivate_channel_btn_text = self.data.message.button_channel_disactivate
            disactivate_channel_btn_callback = self.form_channel_callback(action="Disactivate", channel_id=channel_id)
            disactivate_channel_btn = InlineKeyboardButton(text=disactivate_channel_btn_text, callback_data=disactivate_channel_btn_callback)
            buttons += [disactivate_channel_btn]

        # change photo
        change_photo_btn_text = self.data.message.button_channel_change_photo
        change_photo_btn_callback = self.form_channel_callback(action="ChangePhoto", channel_id=channel_id)
        change_photo_btn = InlineKeyboardButton(text=change_photo_btn_text, callback_data=change_photo_btn_callback)
        buttons += [change_photo_btn]

        # change tag
        change_tag_btn_text = self.data.message.button_channel_change_tag
        change_tag_btn_callback = self.form_channel_callback(action="TagList", channel_id=channel_id)
        change_tag_btn = InlineKeyboardButton(text=change_tag_btn_text, callback_data=change_tag_btn_callback)
        buttons += [change_tag_btn]

        # change description
        change_description_btn_text = self.data.message.button_channel_change_description
        change_description_btn_callback = self.form_channel_callback(action="ChangeDescription", channel_id=channel_id)
        change_description_btn = InlineKeyboardButton(text=change_description_btn_text, callback_data=change_description_btn_callback)
        buttons += [change_description_btn]

        # change price
        change_price_btn_text = self.data.message.button_channel_change_price
        change_price_btn_callback = self.form_channel_callback(action="ChangePrice", channel_id=channel_id)
        change_price_btn = InlineKeyboardButton(text=change_price_btn_text, callback_data=change_price_btn_callback)
        buttons += [change_price_btn]

        # update stats
        change_stats_btn_text = self.data.message.button_channel_change_stats
        change_stats_btn_callback = self.form_channel_callback(action="UpdateStatisticChannel", channel_id=channel_id)
        change_stats_btn = InlineKeyboardButton(text=change_stats_btn_text, callback_data=change_stats_btn_callback)
        buttons += [change_stats_btn]

        return buttons

    def create_channel_button(self, channel):
        def cut_channel_name(name):
            if len(name) > self.MAX_CHANNEL_LENGTH:
                cut_name = name[:self.MAX_CHANNEL_LENGTH] + "..."
                return cut_name
            return name
         
        channel_btn_text = cut_channel_name(name=channel.Name)
        channel_btn_callback = self.form_channel_callback(action="Select", channel_id=channel.ChannelID)
        channel_btn = InlineKeyboardButton(text=channel_btn_text, callback_data=channel_btn_callback)

        return channel_btn

    def form_channel_statistic(self, channel_name, subscribers, posts_number=500):
        """Form the statistic of the channel based on it`s posts

        Parameters
        ----------
        channel_name : str
            Name of the channel\n
        subscribers : int
            The amount of subscribers in channel\n
        posts_number : int, optional
            The amount of posts to analyse
        
        Returns
        -------
        tuple : 
            avg views for last {posts_number} posts\n
            avg views for last 24 hours\n
            ER for last {posts_number} posts\n
            ER for last 24 hours\n
        """
        posts = self.client.get_messages(channel_name=channel_name, limit=posts_number)

        #remove last post
        #posts.pop(0)

        #find all post for last seven day
        posts_for_last_seven_days = list()
        seven_days_ago = (datetime.now() - timedelta(days=7)).replace(tzinfo=timezone.utc)
        for post in posts:
            if post.date > seven_days_ago or (post.date.day == seven_days_ago.day and post.date.hour >= seven_days_ago.hour):
                posts_for_last_seven_days += [post]
            else:
                break
        #form statistic for last 7 days
        if len(posts_for_last_seven_days) != 0:
            views_all = [post.views for post in posts_for_last_seven_days if post.views]
            posts_number_all = len(views_all)
            avg_views_all = int(sum(views_all) / posts_number_all)
            er_all = round((avg_views_all / subscribers) * 100, 2)
        else:
            avg_views_all = 0
            er_all = 0

        #find all post for last day
        posts_for_last_day = list()
        yesterday = (datetime.now() - timedelta(days=1)).replace(tzinfo=timezone.utc)
        for post in posts:
            if post.date > yesterday or (post.date.day == yesterday.day and post.date.hour >= yesterday.hour):
                posts_for_last_day += [post]
            else:
                break
                
        #form statistic for last day
        if len(posts_for_last_day) != 0:
            views_for_last_day = [post.views for post in posts_for_last_day if post.views]
            posts_number_for_last_day = len(views_for_last_day)
            avg_views_for_last_day = int(sum(views_for_last_day) / posts_number_for_last_day)
            er_for_last_day = round((avg_views_for_last_day / subscribers) * 100, 2)
        else:
            avg_views_for_last_day = 0
            er_for_last_day = 0

        return (avg_views_all, avg_views_for_last_day, er_all, er_for_last_day)