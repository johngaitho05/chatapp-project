# Generated by Django 2.2.6 on 2020-06-26 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0021_auto_20200518_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='chat_room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.ChatRoom'),
        ),
    ]
