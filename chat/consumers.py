# chat/consumers.py
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import WebsocketConsumer
from datetime import datetime
import json
from .models import Message
from .views import update_last_message, update_receiver_contacts, get_or_create

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'time': str(datetime.strftime(message.timestamp, '%H:%M'))
        }

    def new_message(self, data):
        author_username = data['from']
        content = data['message']
        author_user = get_object_or_404(User, username=author_username)
        room_name = data["room_name"]
        chat_room = get_or_create(room_name)
        current_time = datetime.strptime(data['current_time'], '%d-%m-%Y %H:%M:%S')
        message = Message.objects.create(author=author_user,
                                         content=content, chat_room=chat_room, timestamp=current_time)
        update_last_message(chat_room)
        update_receiver_contacts(author_user, room_name)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message),
            'last_text': message.sliced_content()
        }
        self.send_chat_message(content)

    commands = {
        # 'fetch_messages':fetch_messages,
        'new_message': new_message,
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        async_to_sync(self.accept())

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # sending message to the channel
    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
