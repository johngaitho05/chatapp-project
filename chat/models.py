from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Contact(models.Model):
    saver = models.ForeignKey(User, related_name="contact_saver", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name="associated_user", on_delete=models.CASCADE)
    saved_as = models.CharField(max_length=50)

    def __str__(self):
        return self.owner.username + ' __saved by__ ' + self.saver.username+'__as__'+self.saved_as


class Message(models.Model):
    author = models.ForeignKey(User, related_name="user_messages", on_delete=models.DO_NOTHING)
    content = models.TextField()
    timestamp = models.DateTimeField()
    chat_room = models.ForeignKey("ChatRoom", on_delete=models.CASCADE)

    def __str__(self):
        return self.author.username

    def sliced_content(self):
        return self.content[:40]


class ChatRoom(models.Model):
    name = models.CharField(max_length=50)
    last_message = models.ForeignKey(Message, related_name='chatroom_last_message',
                                     null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name)
