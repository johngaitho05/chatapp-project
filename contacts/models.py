from django.db import models
import django


class Contact(models.Model):
    user = models.CharField(max_length=100)
    phone= models.CharField(max_length=20)
    name= models.CharField(max_length=100)
    last_message = models.TextField(default=' ')

    def __str__(self):
        return self.name


class Message(models.Model):
    content  = models.TextField(default=' ')
    time = models.DateTimeField(("Time"), default=django.utils.timezone.now)
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)

    def __str__(self):
        return self.sender




