from django.db import models
from datetime import date,time,datetime
import django


class Contact(models.Model):
    user = models.CharField(max_length=100)
    phone= models.CharField(max_length=20)
    name= models.CharField(max_length=100)
    last_message = models.TextField(default=' ')

    def __str__(self):
        return self.name


class Message(models.Model):
    content = models.TextField(default=None)
    date = models.DateField(("Date"), default=date.today())
    time = models.TimeField(("Time"),default=datetime.now().strftime("%H:%M"))
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)

    def __str__(self):
        return self.sender




