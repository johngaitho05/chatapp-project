
from django.db import models
from datetime import date,time,datetime
from django.contrib.auth import get_user_model
from datetime import datetime
import django

User = get_user_model()


class Contact(models.Model):
    user = models.ForeignKey(User, related_name="user_contacts",on_delete=models.CASCADE)
    phone= models.CharField(max_length=20)
    name= models.CharField(max_length=100)
    last_message = models.TextField()

    def __str__(self):
        return self.name


class Message(models.Model):
    author = models.ForeignKey(User, related_name="user_messages",on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    time = models.CharField(max_length=10, default=str(datetime.now().strftime("%H:%M")))
    chat_room = models.CharField(max_length=50)

    def __str__(self):
        return self.author.username


class ChatRoom(models.Model):
    slot = models.IntegerField()
    rooms = models.TextField()

    def __str__(self):
        return str(self.slot)








