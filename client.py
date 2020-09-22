from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import functions
import asyncio

class Client:
    
    CLIENT_API_ID = 1676339 
    CLIENT_API_HASH = "617d050711d1b41e778d112ebdc43a49"

    SESSION_STRING = "1ApWapzMBuzd-ZeqOqUkeu__uAckHpklYb9X2hykvl1oDiiEOpOp-TWnmCo0VAifiDBOMrQNIE75CQ3IiXTWKNaTP3NKdracIXe6z6OZmF1v6efiUDyQjizJUFlZePAXtY618MeJ87olfRkXd-xkIqFQhHNWzAz3TwP0MK-5XRrb2IXyfmzpEYEl6c-3F4lf_y3MB4wudbktbPuDkPticJd3rhkexk8izJsnVkvyFi8ZNY_s7Uhbb1Roa47Tf2UejUIbXJKIt1UFhrFcv-1iiLBj3yuQUEJqH9ZIJowNYIrDogtRwERtVzCPxG5_-_HAFRlLtPXxfoSGvguVLICR6GPTKI2GJALI="
    
    def __init__(self, data=None):
        self.data = data

    def get_channel(self, channel_name):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        text = None
        channel = None

        try:
            with TelegramClient(StringSession(self.SESSION_STRING), self.CLIENT_API_ID, self.CLIENT_API_HASH) as client:
                channel = client(functions.channels.GetFullChannelRequest(channel=channel_name))
        except TypeError:
            text = self.data.message.channel_not_channel
            channel = None
        except ValueError:
            text = self.data.message.channel_not_exist
            channel = None
        except:
            return channel, text####################    NOTIFY OWNER ABOUT ERRROR
        
        return channel, text

    def send_register_instructions(self, owner_username):
        with TelegramClient(StringSession(self.SESSION_STRING), self.CLIENT_API_ID, self.CLIENT_API_HASH) as client:
            client.send_message(owner_username, "Я\n\n\nКидаю\nІнстуркції")

    def get_messages(self, channel_name, limit=10):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        with TelegramClient(StringSession(self.SESSION_STRING), self.CLIENT_API_ID, self.CLIENT_API_HASH) as client:
            return client.get_messages(channel_name, limit=limit)

    def get_post_views_number(self, channel_name, message_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        with TelegramClient(StringSession(self.SESSION_STRING), self.CLIENT_API_ID, self.CLIENT_API_HASH) as client:
            try:
                message = client.get_messages(channel_name, offset_id=message_id+1)[0]
            except:
                message = None
            return message.views
