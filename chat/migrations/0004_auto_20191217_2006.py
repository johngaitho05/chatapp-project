# Generated by Django 2.2.6 on 2019-12-17 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20191215_1905'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='chatroom',
            new_name='chat_room',
        ),
        migrations.AlterField(
            model_name='message',
            name='time',
            field=models.CharField(default='20:05', max_length=10),
        ),
    ]
